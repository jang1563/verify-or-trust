"""LLM-free baseline policies on the panels — the pre-registered value proof (K1).

A policy chooses a verify-set S of genes to assay. Verified genes are answered correctly; unverified genes are
answered by the foundation model (correct iff `fm_correct`). So accuracy = 1 - (FM-wrong genes NOT verified)/N,
and the only way to gain accuracy is to spend the assay on FM-WRONG genes. net = #correct - lambda*#assays.

K1 (the benchmark only has teeth if this passes): directed allocation (oracle / FM-magnitude) must beat random
on accuracy-per-assay by a clear margin. Run this BEFORE any LLM.
"""
from __future__ import annotations

import json

import numpy as np

__all__ = ["load_panels", "run_baselines"]


def load_panels(path: str) -> list[dict]:
    return [json.loads(line) for line in open(path) if line.strip()]


def _acc_cost(panel: list[dict], verify_idx) -> tuple[int, int]:
    S = set(verify_idx)
    n_correct = sum(1 for i, g in enumerate(panel) if i in S or g["fm_correct"])
    return n_correct, len(S)


def _wrong_idx(panel: list[dict]) -> list[int]:
    return [i for i, g in enumerate(panel) if not g["fm_correct"]]


def run_baselines(panels: list[dict], lam: float = 0.5, seed: int = 0,
                  k1_min_gap: float = 0.10) -> dict:
    """Return baseline metrics + the K1 verdict. Deterministic given `seed`."""
    rng = np.random.default_rng(seed)

    def run(policy, reps=1):
        accs, des, nets = [], [], []
        for pan in panels:
            gs = pan["panel"]
            n = len(gs)
            for _ in range(reps):
                S = policy(gs)
                nc, nd = _acc_cost(gs, S)
                accs.append(nc / n)
                des.append(nd / n)
                nets.append(nc - lam * nd)
        return dict(accuracy=float(np.mean(accs)), assays_per_gene=float(np.mean(des)), net=float(np.mean(nets)))

    fixed = {
        "trust-all": lambda gs: [],
        "brute-force": lambda gs: list(range(len(gs))),
        "oracle": lambda gs: _wrong_idx(gs),
    }
    results = {name: run(p) for name, p in fixed.items()}

    # efficiency frontier: random vs FM-magnitude vs oracle-capped, at budget K = frac*N
    frontier = {}
    for frac in (0.1, 0.2, 0.3, 0.4, 0.5):
        def rand_k(gs, _f=frac):
            k = max(1, round(_f * len(gs)))
            return list(rng.permutation(len(gs))[:k])

        def mag_k(gs, _f=frac):
            k = max(1, round(_f * len(gs)))
            return list(np.argsort([-abs(g["fm_log2FC"]) for g in gs])[:k])

        def oracle_k(gs, _f=frac):
            k = max(1, round(_f * len(gs)))
            return _wrong_idx(gs)[:k]

        frontier[frac] = {"random": run(rand_k, reps=5), "fm_magnitude": run(mag_k),
                          "oracle_capped": run(oracle_k)}

    # K1: at the oracle's natural budget (mean #wrong), does directed allocation beat random?
    mean_wrong_frac = float(np.mean([pan["n_wrong"] / pan["n_panel"] for pan in panels]))

    def rand_atwrong(gs):
        k = max(1, round(mean_wrong_frac * len(gs)))
        return list(rng.permutation(len(gs))[:k])

    oracle_acc = results["oracle"]["accuracy"]
    random_acc = run(rand_atwrong, reps=5)["accuracy"]
    gap = oracle_acc - random_acc
    k1 = {"mean_wrong_frac": mean_wrong_frac, "oracle_acc": oracle_acc, "random_acc": random_acc,
          "gap": gap, "passed": bool(gap >= k1_min_gap)}
    return {"policies": results, "frontier": frontier, "k1": k1, "lam": lam, "n_panels": len(panels)}
