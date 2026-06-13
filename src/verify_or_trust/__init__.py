"""Verify-or-Trust — a verifiable-reward agentic benchmark for biology foundation-model orchestration.

The question: given a foundation model's prediction of a perturbation's effects, does an LLM correctly decide
*where to trust the model vs. run the real (costly) assay* — i.e. allocate verification to the genes where the
foundation model is actually wrong? Graded by a held-out real experiment = verifiable reward.

Public API is intentionally small; see the submodules:
  - panels:     build stratified per-perturbation evaluation panels from a substrate
  - baselines:  LLM-free policies (trust-all / brute / random / FM-magnitude / oracle) — the value proof (K1)
  - env:        the agentic tool-use environment (run_de, query_gene, equivalence_test, submit)
  - grade:      metrics (net reward, verification precision/recall, capability spectrum)
  - substrates: builders that download from source (GEARS/Norman, Arc STATE/Tahoe)
"""

__version__ = "0.1.0"
