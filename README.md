# Verify-or-Trust

![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-Apache--2.0-green)
![ci](https://github.com/jang1563/verify-or-trust/actions/workflows/ci.yml/badge.svg)
![reproducible](https://img.shields.io/badge/reproducible-make%20reproduce-green)

**A verifiable-reward agentic benchmark: when an LLM orchestrates a fallible biology foundation model, does it
know where to _trust_ the model versus _run the real experiment_?**

📋 Data schemas & a programmatic-API example: [`SCHEMA.md`](SCHEMA.md) · [`examples/quickstart.py`](examples/quickstart.py).
Findings & honest limitations: [`CARD.md`](CARD.md). Build/verify process: [`RELEASE.md`](RELEASE.md).

A perturbation foundation model (e.g. GEARS, Arc STATE) predicts which genes a perturbation changes — fast, but
sometimes confidently wrong. An LLM agent is given those predictions, a panel of candidate genes, and a costly
`run_de` tool that executes a **real differential-expression analysis on perturb-seq cells**. It must decide
*which genes to verify* and submit a final call for each. The reward is verifiable — graded against a held-out
real experiment — and the cost of the assay makes **verification allocation** the skill under test: spend the
budget where the foundation model is actually wrong.

> Built with a verification gate at every step (`RELEASE.md`): a clean clone reproduces the LLM-free value proof
> with `make reproduce`, every metric is backed by a test or a one-command run, and no third-party data is
> redistributed. Private during review; a preprint is in preparation.

## Why this benchmark
Most agentic-bio evals score whether the model gets the answer. This one isolates a capability that decides
whether LLM × foundation-model pipelines actually work in practice: **calibrated verification** — using an
expensive ground-truth tool *selectively*, where a cheap predictor is unreliable. It comes with:
- a **verifiable reward** (held-out perturbation) — usable for eval *and* RL,
- an **LLM-free value proof** (baselines must separate good vs bad allocation before any model is run),
- **two substrates** — GEARS/Norman (public) and Arc STATE/Tahoe (a real released foundation model),
- **genuine execution** — `run_de` runs a real DE on the cells; `query_gene` hits a real gene database.

## Headline finding (research runs)
![Capability inversion: the strongest model is the worst orchestrator; a reliability signal fixes it, domain
knowledge does not](results/capability_inversion.png)

Frontier models **do not allocate verification** to where the foundation model errs — they over-verify, and
*more capable models over-verify more*, so under a realistic assay cost the strongest model is the **worst**
orchestrator (capability inversion). Domain knowledge (`query_gene`) does not fix it; an explicit per-gene
reliability signal does (they follow it near-perfectly). **The bottleneck is the foundation model exposing
calibrated uncertainty, not the LLM's reasoning.**

| GEARS/Norman, 107 panels, λ=0.5 | accuracy | assays | net | verify-precision |
|---|---:|---:|---:|---:|
| trust-all (never verify) | 68% | 0% | 17.8 | — |
| Haiku 4.5 | 82% | 39% | 16.2 | 38% |
| Sonnet 4.6 | 87% | 47% | 16.6 | 44% |
| Opus 4.8 | 96% | 78% | **14.9** | 36% |
| oracle (verify iff FM wrong) | 100% | 32% | **21.9** | 100% |

*All rows are the deduplicated 107-panel run (2026-06-13); trust-all/oracle reproduce LLM-free via `make reproduce`, the model rows via `vot run`.*

Verify-precision ≈ the 32% base rate → no targeting; the **frontier** model (Opus) over-verifies 78% and nets
**least** — significantly below both smaller models (Opus−Haiku t=−4.70, Opus−Sonnet t=−6.48, p<10⁻⁴) and below just
trusting the FM. Add a learned reliability signal and net rises + the inversion disappears. Full tables + caveats:
[`results/RESULTS.md`](results/RESULTS.md) · [`CARD.md`](CARD.md).

## Install
```bash
git clone https://github.com/jang1563/verify-or-trust && cd verify-or-trust
pip install -e .            # core (panels, baselines, grading)
pip install -e ".[agent]"   # + the LLM agent loop (Anthropic SDK)
```

## Quickstart
The GEARS/Norman substrate ships in the repo, so panels + the LLM-free value proof run with no downloads:
```bash
make reproduce                                                     # vot panels + vot baselines (K1) — deterministic
# or explicitly:
vot panels    --substrate-table data/substrates/gears_norman.csv --out runs/panels.jsonl
vot baselines --panels runs/panels.jsonl                          # LLM-free value proof (K1)
```
For the agent run + the live `run_de` tool, fetch the perturb-seq cells from the dataset and provide a key:
```bash
huggingface-cli download jang1563/verify-or-trust --repo-type dataset --local-dir vot_data  # cells (+substrates)
export ANTHROPIC_API_KEY=...
vot run   --panels runs/panels.jsonl --model <model> --real-de vot_data/cells/norman_subset.h5ad --out runs/ep.jsonl
vot grade --panels runs/panels.jsonl --episodes runs/ep.jsonl
```

Data: **[`jang1563/verify-or-trust`](https://huggingface.co/datasets/jang1563/verify-or-trust)** (Hugging Face
dataset — substrate tables + cells).

## Substrates
- **`gears_norman`** (public) — ships in the repo (`data/substrates/gears_norman.csv`); runs out of the box.
- **`state_tahoe`** (Arc, **non-commercial**) — build it from Arc's released model outputs (you accept Arc's terms):
  ```bash
  vot build-substrate --substrate state_tahoe --out data/substrates/state_tahoe.csv   # downloads from Arc HF
  vot panels --substrate-table data/substrates/state_tahoe.csv --out runs/tahoe.jsonl
  ```

## Data & licensing
The benchmark **code** is Apache-2.0. Third-party data is **not redistributed** — Norman 2019 (public, via GEARS)
and Arc STATE/Tahoe (Arc's Hugging Face repo, under Arc's **non-commercial** Model License + Acceptable Use Policy)
are downloaded from source by the builders. See [`data/README.md`](data/README.md). Results: [`results/RESULTS.md`](results/RESULTS.md).

## Citation
See [`CITATION.cff`](CITATION.cff). A preprint describing the benchmark and findings is in preparation.

## License
Apache-2.0 (code). Third-party data retains its own license (see above).
