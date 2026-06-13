# Verify-or-Trust

**A verifiable-reward agentic benchmark: when an LLM orchestrates a fallible biology foundation model, does it
know where to _trust_ the model versus _run the real experiment_?**

A perturbation foundation model (e.g. GEARS, Arc STATE) predicts which genes a perturbation changes — fast, but
sometimes confidently wrong. An LLM agent is given those predictions, a panel of candidate genes, and a costly
`run_de` tool that executes a **real differential-expression analysis on perturb-seq cells**. It must decide
*which genes to verify* and submit a final call for each. The reward is verifiable — graded against a held-out
real experiment — and the cost of the assay makes **verification allocation** the skill under test: spend the
budget where the foundation model is actually wrong.

> Status: **research preview (private).** The harness is being ported from the research code with a verification
> gate at each step (see `RELEASE.md`); numbers below are from the research runs and are reproduced in-repo as
> each component lands.

## Why this benchmark
Most agentic-bio evals score whether the model gets the answer. This one isolates a capability that decides
whether LLM × foundation-model pipelines actually work in practice: **calibrated verification** — using an
expensive ground-truth tool *selectively*, where a cheap predictor is unreliable. It comes with:
- a **verifiable reward** (held-out perturbation) — usable for eval *and* RL,
- an **LLM-free value proof** (baselines must separate good vs bad allocation before any model is run),
- **two substrates** — GEARS/Norman (public) and Arc STATE/Tahoe (a real released foundation model),
- **genuine execution** — `run_de` runs a real DE on the cells; `query_gene` hits a real gene database.

## Headline finding (research runs)
Frontier models **do not allocate verification** to where the foundation model errs — they over-verify, and
*more capable models over-verify more*, so under a realistic assay cost the strongest model is the **worst**
orchestrator (capability inversion). Domain knowledge (`query_gene`) does not fix it; an explicit per-gene
reliability signal does (they follow it near-perfectly). **The bottleneck is the foundation model exposing
calibrated uncertainty, not the LLM's reasoning.** Full results and the honest caveats are in [`CARD.md`](CARD.md).

## Install
```bash
git clone <repo> && cd verify-or-trust
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

## Data & licensing
The benchmark **code** is Apache-2.0. Input data is **not redistributed** — substrate builders download it from
source: Norman 2019 (public, via GEARS) and Arc STATE/Tahoe (Arc's Hugging Face repo, under Arc's **non-commercial**
Model License + Acceptable Use Policy, which you must accept). See [`data/README.md`](data/README.md).

## Citation
See [`CITATION.cff`](CITATION.cff). A preprint describing the benchmark and findings is in preparation.

## License
Apache-2.0 (code). Third-party data retains its own license (see above).
