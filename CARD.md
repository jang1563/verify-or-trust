# Benchmark card — Verify-or-Trust

> Numbers are from runs on Anthropic Haiku 4.5 / Sonnet 4.6 / Opus 4.8 (2026-06), reproducible via the harness
> (`vot run` / `make reproduce`). Read with the **Limitations** section — it is not an afterthought.

## Task
Given a perturbation, a readout panel of N genes, and a foundation model's predicted effect per gene, an LLM
agent decides which genes to **verify** with a costly `run_de` tool (a real differential-expression assay,
perturbation vs control cells) and submits a final call (effect↑/effect↓/no-effect/untested) for every gene.
Reward = (correct calls) − λ·(genes assayed). The held-out real experiment is the verifiable ground truth.

## Why it is hard / what it isolates
Trusting the cheap predictor everywhere is wrong (it errs); verifying everything is wasteful (the assay costs).
The skill is **verification allocation**: assay the genes where the predictor is actually wrong. Panels are
stratified so a directed allocator provably beats random/brute-force (the pre-registered K1 gate).

## Metrics
- **net reward** = correct − λ·assays (headline; report a λ-sweep).
- **verify-precision / recall** = of assayed genes, fraction the FM was wrong on / of FM-wrong genes, fraction
  assayed (the allocation quality; base-rate-referenced).
- **accuracy vs random@budget**: model accuracy minus a random allocator's at the same assay count.
- **capability spectrum**: where models land between trust-all and oracle.

## Baselines (LLM-free)
trust-all, brute-force, random-K, FM-magnitude, oracle. K1: oracle beats random by ≈ +21% accuracy at equal cost
on GEARS/Norman (107 deduped panels; and the FM-magnitude heuristic is *worse* than random — a substrate property).

## Substrates
- **gears_norman** (public): GEARS on Norman 2019; live `run_de` on 91k cells; real gene symbols (`query_gene`
  available).
- **state_tahoe** (Arc, non-commercial): Arc STATE/ST-HVG-Tahoe released predictions vs real DE; the same finding
  replicates on a real released foundation model and a drug-perturbation modality.

## Findings (research)
- **No model allocates well**; verify-decision predicts FM-wrongness only weakly (AUC 0.56–0.59).
- **Frontier-model inversion (cost-conditional)**: assay rate rises with capability (Haiku 39% → Opus 78%) but
  targeting does not, so *once verification is costly* the frontier model (Opus) nets *least* — at λ=0.5 significantly
  below both smaller models (paired Opus−Haiku −1.38 t=−4.70; Opus−Sonnet −1.78 t=−6.48; p<10⁻⁴), which tie. The sign
  is cost-dependent: at λ=0.2 Opus is *best* (cheap verification pays off); the inversion appears at λ≥0.5 and deepens.
  (Significant on the clean re-run; dedup and harness changed together, so we don't attribute the effect size to dedup.)
- **A per-gene reliability signal fixes it**: given one (even an imperfect learned one, AUC 0.70), models follow
  it near-fully (94–99% of assays) → targeting and net rise, inversion reverses; orchestration net scales with
  the **signal's** quality, not the LLM's. **Domain knowledge (`query_gene`) does not fix allocation.**
- Read-through: the bottleneck is the foundation model exposing calibrated per-input uncertainty, and the LLM is
  a faithful — but uncritical — follower of whatever reliability signal it is given.

## Intended use
Evaluating (and, via the verifiable reward, post-training toward) calibrated tool-use / verification in agentic
biology pipelines. Diagnosing where LLM × foundation-model orchestration breaks down.

## Limitations (do not skip)
- **Weak-not-zero allocation**: models are *barely* above chance at self-estimating reliability, not literally
  random. **Obey-not-reason**: with a signal they defer near-completely (override <6%) — robust to good signals,
  would parrot a bad one. **λ-dependence**: the net inversion holds for non-trivial assay cost; the allocation
  failure itself is λ-independent. **Single un-ablated prompt.** **Tool-noise**: the live `run_de` agrees with the
  sceptre reference ≈89% — a real, imperfect assay, not an oracle. **Tahoe** uses anonymized gene indices and a
  50%-wrong panel construction (absolute accuracy is substrate-driven; the *pattern* is what replicates).
- "Dose-response in signal quality" is three monotone points, one of which is a simulated signal.

## Provenance, license, ethics
Code Apache-2.0; data downloaded-from-source, not redistributed (`data/README.md`); Arc STATE is non-commercial.
No human-subjects data. The biology is published perturbation screens. Intended for research on safe, calibrated
agentic systems.
