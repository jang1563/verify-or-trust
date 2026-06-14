# Results (research runs)

Anthropic Haiku 4.5 / Sonnet 4.6 / Opus 4.8, 2026-06. λ = assay cost. Reproduce the LLM-free rows exactly with
`make reproduce`; the LLM rows need an API key (`vot run`) and are **single stochastic runs** (one episode per panel
per model, one seed) — directionally reproducible, not bit-exact. Read with [`CARD.md`](../CARD.md) limitations.

> **Status (2026-06-13):** all rows are refreshed on **deduplicated** substrates — GEARS/Norman (107 panels, seed 13: K1, frontier-model + λ-sweep, reliability-signal via `vot run --reliability-flags`, `query_gene`, live-execution), Tahoe (160 panels: cross-substrate echo), and the RL/probe extension. One row stays tagged: the **+perfect-signal** ceiling *[research-only]* (uses ground truth, excluded from the public harness).

## K1 — the value proof (LLM-free, GEARS/Norman, 107 panels)
| policy | accuracy | assays/gene | net@λ0.5 |
|---|---:|---:|---:|
| trust-all | 68.1% | 0% | 17.81 |
| brute-force | 100% | 100% | 12.98 |
| **oracle** | 100% | 32% | **21.88** |

Oracle beats a random allocator by **+21.4%** accuracy at equal budget; the FM-magnitude heuristic is *worse*
than random (the FM errs at low predicted magnitude). The benchmark discriminates allocation strategy.

## Frontier models — no allocation, capability inversion (GEARS/Norman)
| model | accuracy | assays | net@λ0.5 | verify-precision | rand@budget |
|---|---:|---:|---:|---:|---:|
| Haiku | 81.5% | 39% | 16.24 | 38% | 80.9% |
| Sonnet | 87.2% | 47% | 16.64 | 44% | 83.5% |
| Opus | 95.8% | 78% | **14.86** | 36% | 93.5% |

Verify-precision sits near the base rate (~32%) for every model — **no targeting**; accuracy ≈ a random allocator at
the same budget. Assay rate rises with capability (Haiku 39% → Opus 78%) while targeting does not, so once
verification is costly the **frontier** model nets least: at λ=0.5, paired **Opus−Haiku −1.38 (t=−4.70)** and
**Opus−Sonnet −1.78 (t=−6.48)**, p<10⁻⁴ (Haiku ≈ Sonnet, n.s.).

**The inversion is cost-conditional** — it is the over-verification, not capability per se, that costs:
| net by λ | λ=0.2 | λ=0.5 | λ=0.8 |
|---|---:|---:|---:|
| Haiku | 19.27 | 16.24 | 13.22 |
| Sonnet | 20.26 | 16.64 | 13.01 |
| **Opus** | **20.88** | 14.86 | 8.84 |

When verification is cheap (λ=0.2) Opus's heavy verifying *pays off* and it is the **best** orchestrator; the
inversion appears only once the assay cost is non-trivial (λ ≥ 0.5) and deepens as λ grows. So the honest headline is
conditional: *under a non-trivial verification cost*, the most capable model is the worst orchestrator. (The t-tests
are significant on the clean re-run; we do **not** attribute the effect size to deduplication specifically — the
clean run also changed harness, so dedup and harness are confounded.)

## A reliability signal fixes it; domain knowledge does not (GEARS/Norman)
| condition | vPrecision | net@λ0.5 (Opus) | notes |
|---|---:|---:|---|
| no signal | 36% | 14.86 | frontier over-verifies (78% assay), nets least |
| **+ learned trust-head signal (AUC 0.70)** | **47%** | **17.28** | assay 78%→44%, targeting ↑, net ↑; inversion removed |
| + `query_gene` domain knowledge | 35% | 14.11 | no targeting gain (vPrec ≈ base); assay ↑ 87%, net ↓ |
| + perfect-ish signal (AUC ~0.85) *[research-only]* | 59–64% | 17.03 | upper bound; uses ground truth, excluded from the public harness |

Orchestration net scales with the **signal's** quality while the LLM follows near-fully — the bottleneck is the
foundation model exposing calibrated uncertainty, not the LLM's reasoning (which it does not critically evaluate).

## Holds under real execution + a real Arc model
- **Live `run_de`** (DE computed on the Norman cells; 89% agreement with the sceptre reference; clean 107 panels):
  findings hold and sharpen — Opus 12.44 < Haiku 15.04 net, both below trust-all 17.81 (over-verifying an imperfect
  assay costs more).
- **Arc STATE / Tahoe** (a real released foundation model, drug modality; 160 panels, deduplicated 2026-06-13):
  the over-verification **mechanism echoes**, but the capability ordering does *not* transfer cleanly. At λ=0.5 the
  strongest model nets below the weakest (Opus 6.82 < Haiku 10.46), with no targeting (vPrec at base) and assay rising
  with capability (Haiku 37% → Opus 64%). Across the λ-sweep the **weakest** model (Haiku) is best at *every* cost
  while the two larger models stay below it and even swap order with λ — i.e. "weakest-model-best," not a monotone
  ladder; Sonnet also hedges 24% of calls to *untested* on this harder integer-gene-id substrate. What crosses
  substrates is the **mechanism** (capability buys no targeting; over-verifying is punished under cost), not the ladder.

## Can RL *train* an orchestrator to allocate? (extension — a verifiable-reward study)
The reward here is verifiable, so the env doubles as an RL gym. We trained a small policy (Qwen2.5-7B, LoRA, GRPO)
with a proper-scoring (RLCR-style) verifiable reward + a binary-reward ablation, GroupKFold-OOD by perturbation.

| policy (per-edge, held-out perts) | verify-AUC | net | verify-rate |
|---|---:|---:|---:|
| cold 7B | 0.47 | 0.49 | 94% (over-verifies) |
| RL (proper-scoring, 250 steps) | 0.51 | 0.53 | 0% (collapses to trust-all) |
| external trust-head (HistGBM) | **0.71** | **0.63** | — |
| **linear probe on the cold 7B's hidden states** | **0.67** | — | — |

RL does **not** internalize the signal — it converges to the trivial trust-all policy (net = always-trust). But a
linear probe on the cold model's *representation* recovers the signal at **AUC 0.67** (≈ the GBM, far above the RL'd
policy 0.51): the reliability signal is **present and recoverable in the LLM — RL just fails to surface it into
behavior** (a policy-extraction failure, not a representation one). Deployable takeaway: **read the signal out** (an
external classifier, or a probe of the orchestrator's hidden states) rather than relying on the behavioral policy —
the same conclusion the frontier-model rows reach from the opposite (over-verifying) direction.
