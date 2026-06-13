# Results (research runs)

Anthropic Haiku 4.5 / Sonnet 4.6 / Opus 4.8, 2026-06. λ = assay cost. Reproduce the LLM-free rows with
`make reproduce`; the LLM rows need an API key (`vot run`). Read with [`CARD.md`](../CARD.md) limitations.

> **Status (2026-06-13):** the **K1 (LLM-free)** and **frontier-model** rows are refreshed on the **deduplicated** substrate (107 panels, seed 13; `make reproduce` for K1, `vot run` for the frontier episodes); the **RL/probe** extension is on deduplicated data. The **reliability-signal** and **live-execution** rows are still from the pre-dedup run (110 panels) and tagged *[pre-dedup]* — a full re-baseline of those conditions is a public-flip item.

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
the same budget. Assay rate rises with capability (Haiku 39% → Opus 78%) while targeting does not, so under cost the
**frontier** model nets least: paired **Opus−Haiku −1.38 (t=−4.70, p<10⁻⁴)** and **Opus−Sonnet −1.78 (t=−6.48,
p<10⁻⁴)**; Haiku and Sonnet tie (n.s.). The most capable model is the worst orchestrator — a significant
**frontier-model inversion** (not a strict monotone trend; the effect *strengthened* on the deduplicated 107-panel set).

## A reliability signal fixes it; domain knowledge does not (GEARS/Norman)
| condition | vPrecision | net@λ0.5 (Opus) | notes |
|---|---:|---:|---|
| no signal *(clean)* | 36% | 14.86 | frontier over-verifies, nets least |
| **+ learned trust-head signal (AUC 0.70)** *[pre-dedup]* | **47–48%** | 15.30 | models follow it 94–99%; inversion removed |
| + perfect-ish signal (AUC ~0.85) *[pre-dedup]* | 59–64% | 17.03 | inversion reversed (Opus best) |
| + `query_gene` domain knowledge *[pre-dedup]* | ~38% | 13.19 | no targeting gain; assay ↑, net ↓ |

Orchestration net scales with the **signal's** quality while the LLM follows near-fully — the bottleneck is the
foundation model exposing calibrated uncertainty, not the LLM's reasoning (which it does not critically evaluate).

## Holds under real execution + a real Arc model
- **Live `run_de`** (DE computed on the Norman cells; 89% agreement with the sceptre reference): findings hold and
  sharpen — Opus 10.43 < Haiku 13.27 net, both below trust-all 16.97 (over-verifying an imperfect assay costs more).
- **Arc STATE / Tahoe** (a real released foundation model, drug modality): the allocation failure and capability
  inversion replicate.

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
