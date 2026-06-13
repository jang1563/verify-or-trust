# Results (research runs)

Anthropic Haiku 4.5 / Sonnet 4.6 / Opus 4.8, 2026-06. λ = assay cost. Reproduce the LLM-free rows with
`make reproduce`; the LLM rows need an API key (`vot run`). Read with [`CARD.md`](../CARD.md) limitations.

## K1 — the value proof (LLM-free, GEARS/Norman, 110 panels)
| policy | accuracy | assays/gene | net@λ0.5 |
|---|---:|---:|---:|
| trust-all | 63.2% | 0% | 16.71 |
| brute-force | 100% | 100% | 13.24 |
| **oracle** | 100% | 37% | **21.60** |

Oracle beats a random allocator by **+23.4%** accuracy at equal budget; the FM-magnitude heuristic is *worse*
than random (the FM errs at low predicted magnitude). The benchmark discriminates allocation strategy.

## Frontier models — no allocation, capability inversion (GEARS/Norman)
| model | accuracy | assays | net@λ0.5 | verify-precision | rand@budget |
|---|---:|---:|---:|---:|---:|
| Haiku | 81.0% | 41% | 14.34 | 43% | 79.9% |
| Sonnet | 90.4% | 61% | 14.14 | 42% | 87.5% |
| Opus | 94.9% | 76% | 13.35 | 39% | 92.4% |

Verify-precision ≈ the 37% base rate (no targeting); accuracy ≈ a random allocator at the same budget. Assay rate
rises with capability but targeting does not, so net **decreases** with capability (paired Opus−Haiku −0.98±0.36,
t=−2.8). Under a non-trivial assay cost the strongest model is the worst orchestrator.

## A reliability signal fixes it; domain knowledge does not (GEARS/Norman)
| condition | vPrecision | net@λ0.5 (Opus) | notes |
|---|---:|---:|---|
| no signal | ~40% | 13.35 | capability inversion |
| **+ learned trust-head signal (AUC 0.70)** | **47–48%** | 15.30 | models follow it 94–99%; inversion removed |
| + perfect-ish signal (AUC ~0.85) | 59–64% | 17.03 | inversion reversed (Opus best) |
| + `query_gene` domain knowledge | ~38% | 13.19 | no targeting gain; assay ↑, net ↓ |

Orchestration net scales with the **signal's** quality while the LLM follows near-fully — the bottleneck is the
foundation model exposing calibrated uncertainty, not the LLM's reasoning (which it does not critically evaluate).

## Holds under real execution + a real Arc model
- **Live `run_de`** (DE computed on the Norman cells; 89% agreement with the sceptre reference): findings hold and
  sharpen — Opus 10.43 < Haiku 13.27 net, both below trust-all 16.97 (over-verifying an imperfect assay costs more).
- **Arc STATE / Tahoe** (a real released foundation model, drug modality): the allocation failure and capability
  inversion replicate.
