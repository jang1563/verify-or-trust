"""Arc STATE / Tahoe substrate (real Arc foundation model; NON-COMMERCIAL license).

Downloads Arc Institute's pretrained ST-HVG-Tahoe released predictions (`*_pred_de.csv`) and the matched real
differential expression (`*_real_de.csv`) from the Arc Hugging Face repo, derives the STATE per-(perturbation,
gene) effect call (predicted significant & |log2FC| >= delta) vs the real call, and outputs the substrate table.

IMPORTANT: Arc's model and released data are under a non-commercial Model License + Acceptable Use Policy. This
builder downloads them at the user's request and does NOT redistribute them; you must accept Arc's terms. Gene
identities in the Tahoe release are indices, so the `query_gene` knowledge tool is unavailable for this substrate.
Wired in release step 3.
"""
from __future__ import annotations

__all__ = ["build_substrate"]


def build_substrate(*args, **kwargs):
    raise NotImplementedError("build_substrate is wired in release step 3")
