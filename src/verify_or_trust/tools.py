"""The environment's tools (genuine execution, not lookups).

  - run_de:          REAL differential expression computed live on perturb-seq cells (perturbation vs control)
  - query_gene:      REAL biological-database lookup (mygene.info -> NCBI/Ensembl/UniProt aggregate), cached
  - equivalence_test: TOST — is an effect of size >= delta excluded?

Wired in release step 6 (ports `p1_live_de` + `p1_query_gene` + the equivalence test).
"""
from __future__ import annotations

__all__ = ["LiveDE", "GeneDB", "equivalence_test"]


class LiveDE:  # noqa: D401
    """Live differential-expression on perturb-seq cells. Wired in step 6."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("LiveDE is wired in release step 6")


class GeneDB:
    """Cached mygene.info gene-annotation lookup. Wired in step 6."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("GeneDB is wired in release step 6")


def equivalence_test(*args, **kwargs):
    raise NotImplementedError("equivalence_test is wired in release step 6")
