"""The environment's tools — genuine execution, not lookups.

  - equivalence_test : TOST — is an effect of size >= delta excluded?
  - LiveDE           : REAL differential expression computed live on perturb-seq cells (perturbation vs control)
  - GeneDB           : REAL biological-database lookup (mygene.info -> NCBI/Ensembl/UniProt aggregate), cached
"""
from __future__ import annotations

import json
import os
import threading
import urllib.parse
import urllib.request

import numpy as np

__all__ = ["equivalence_test", "LiveDE", "GeneDB"]

DELTA = 0.25
_Z90 = 1.644854
_Z95 = 1.959964


def equivalence_test(log2fc: float, se: float, delta: float = DELTA) -> str:
    """TOST three-state: TESTED_NEGATIVE (effect >= delta excluded) / POSITIVE (significant effect) / UNTESTED."""
    if abs(log2fc) + _Z90 * se < delta:
        return "TESTED_NEGATIVE"
    if se > 0 and abs(log2fc) / se > _Z95 and abs(log2fc) >= delta:
        return "POSITIVE"
    return "UNTESTED"


class LiveDE:
    """Compute differential expression LIVE on perturb-seq cells (the `run_de` tool).

    X is expected log1p-normalized; log2FC is computed on the expm1-linear scale (scale-matched to a sceptre
    reference), with a Welch t-test on the (variance-stabilized) log expression.
    """

    def __init__(self, h5ad: str):
        import anndata as ad
        import scipy.sparse as sp
        self._sp = sp
        self.adata = ad.read_h5ad(h5ad)
        self.gene_idx = {str(g): i for i, g in enumerate(self.adata.var["gene_name"])}
        self.cond = self.adata.obs["condition"].astype(str).values
        self.ctrl_idx = np.where(self.cond == "ctrl")[0]
        self.X = self.adata.X

    def _cells(self, perturbation: str) -> np.ndarray:
        parts = [p for p in perturbation.replace("+ctrl", "").split("+") if p and p != "ctrl"]
        cands = ({parts[0], parts[0] + "+ctrl", "ctrl+" + parts[0]} if len(parts) == 1
                 else {"+".join(parts), "+".join(parts[::-1])})
        for c in cands:
            idx = np.where(self.cond == c)[0]
            if len(idx):
                return idx
        return np.array([], dtype=int)

    def run(self, perturbation: str, genes: list[str]) -> dict:
        from scipy import stats
        pidx = self._cells(perturbation)
        if len(pidx) == 0:
            return {g: {"error": "perturbation cells not found"} for g in genes}
        Xc, Xp = self.X[self.ctrl_idx], self.X[pidx]
        out = {}
        for g in genes:
            j = self.gene_idx.get(str(g))
            if j is None:
                out[g] = {"error": "gene not in dataset"}
                continue
            ctrl = np.asarray(Xc[:, j].todense()).ravel() if self._sp.issparse(Xc) else np.asarray(Xc[:, j]).ravel()
            trt = np.asarray(Xp[:, j].todense()).ravel() if self._sp.issparse(Xp) else np.asarray(Xp[:, j]).ravel()
            lfc = float(np.log2((np.expm1(trt).mean() + 1e-2) / (np.expm1(ctrl).mean() + 1e-2)))
            t, p = stats.ttest_ind(trt, ctrl, equal_var=False)
            se = abs(lfc) / abs(t) if t != 0 else float("nan")
            out[g] = {"log2FC": lfc, "se": float(se) if se == se else 0.1, "q": float(p),
                      "n_trt": int(len(trt)), "n_cntrl": int(len(ctrl))}
        return out


class GeneDB:
    """Cached gene-annotation lookup via mygene.info (the `query_gene` tool). Graceful on unresolved symbols."""

    _AA = None  # unused; kept minimal

    def __init__(self, cache_path: str | None = None):
        self.path = cache_path
        self.cache = json.load(open(cache_path)) if cache_path and os.path.exists(cache_path) else {}
        self._lock = threading.Lock()

    def query(self, gene: str) -> dict:
        g = str(gene)
        if g in self.cache:
            return self.cache[g]
        res = {"error": "no annotation found"}
        try:
            q = urllib.parse.quote(f"symbol:{g}")
            url = f"https://mygene.info/v3/query?q={q}&species=human&fields=name,summary,go.BP"
            data = json.load(urllib.request.urlopen(url, timeout=20))  # noqa: S310 (trusted host)
            hits = data.get("hits") or []
            if hits:
                h = hits[0]
                res = {"name": h.get("name", ""), "summary": (h.get("summary") or "no summary")[:400]}
                go = h.get("go", {}).get("BP", [])
                go = go if isinstance(go, list) else [go]
                terms = [x.get("term") for x in go if isinstance(x, dict) and x.get("term")][:5]
                if terms:
                    res["GO_biological_process"] = terms
        except Exception as e:  # noqa: BLE001 (graceful by design)
            res = {"error": f"DB lookup failed: {str(e)[:60]}"}
        with self._lock:
            self.cache[g] = res
        return res

    def save(self) -> None:
        if self.path:
            with self._lock:
                json.dump(self.cache, open(self.path, "w"))

    def prewarm(self, genes: list[str]) -> int:
        for g in genes:
            self.query(g)
        self.save()
        return sum(1 for g in genes if "error" not in self.cache.get(g, {"error": 1}))
