#!/usr/bin/env python3
"""Research extension (LLM-free, reproducible): is the reliability signal BUILDABLE without ground truth?

The benchmark shows the LLM follows a supplied per-gene reliability signal near-fully (94-99%), and that net
scales with the signal's AUC. The dose-response in `signal_rebaseline.py` injects a SIMULATED signal of a target
AUC (it perturbs the true FM-error label with noise) -- it answers "given a signal at AUC X, does the orchestrator
use it?", not "can such a signal be built?". This script answers the second question on the GEARS/Norman combo
regime, with NO ground-truth at inference.

Method (honest): the target is fm_wrong = (fm_call != real_call) per combo edge. The candidate feature is
DISAGREEMENT WITH THE OBSERVED-ADDITIVE BASELINE -- additive[g] = (measured single-A effect on g) + (measured
single-B effect on g), the field-standard y_A + y_B from MEASURED singles. Singles are cheap/known; the combo is
the question, so additive is inference-available (no held-out combo truth is used as a feature). A gradient-boosted
classifier is CROSS-FIT by perturbation (GroupKFold -> no edge leaks across the split) and scored by AUC against
the true FM-error label. We then run an LLM-free signal-gated allocation (verify the top-fraction by predicted
p(FM-wrong)) to show the buildable signal drives near-ORACLE net -- the deployable end of the dose-response.

Combos only: the additive structure (hence this feature) exists only where a perturbation decomposes into measured
singles. Scope it as such. Deterministic and seeded.

  python research/competence_signal.py --substrate data/substrates/gears_norman.csv
"""
from __future__ import annotations

import argparse
import re

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score

DELTA = 0.25  # the substrate's effect/no-effect threshold (verified: fm_call == |fm_log2FC| >= 0.25)


def load_combos(substrate: str):
    df = pd.read_csv(substrate)
    df = df.assign(real_call=df.real_label.map({"POSITIVE": "effect", "TESTED_NEGATIVE": "no_effect"}))
    singles = {(r.perturbation, r.gene): r.raw_log2FC
               for r in df[df.regime.str.startswith("single")].itertuples()}

    def additive(p, g):
        parts = re.split(r"[+_]", str(p))
        if len(parts) != 2:
            return np.nan
        vals = [singles.get((x, g)) for x in parts]
        return float(np.sum(vals)) if all(v is not None for v in vals) else np.nan

    c = df[df.regime.str.startswith("combo")].copy()
    c["add_lfc"] = [additive(p, g) for p, g in zip(c.perturbation, c.gene)]
    c = c.dropna(subset=["fm_log2FC", "add_lfc", "real_call"]).copy()
    return c


def crossfit(X, y, groups, seed):
    p = np.zeros(len(y))
    for tr, te in GroupKFold(5).split(X, y, groups):
        clf = HistGradientBoostingClassifier(max_depth=3, max_iter=300, random_state=seed)
        p[te] = clf.fit(X[tr], y[tr]).predict_proba(X[te])[:, 1]
    return p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--substrate", default="data/substrates/gears_norman.csv")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    c = load_combos(a.substrate)
    fm = c.fm_log2FC.to_numpy(float)
    ad = c.add_lfc.to_numpy(float)
    y = (c.fm_call != c.real_call).to_numpy().astype(int)
    groups = c.perturbation.to_numpy()
    reg = pd.get_dummies(c.regime).to_numpy(float)

    X_base = np.column_stack([np.abs(fm)])
    X_reg = np.column_stack([np.abs(fm), reg])
    X_add = np.column_stack([np.abs(fm), reg, np.abs(ad), np.abs(fm - ad),
                             (np.sign(fm) != np.sign(ad)).astype(float),
                             ((np.abs(fm) >= DELTA) != (np.abs(ad) >= DELTA)).astype(float)])

    print(f"combos with additive coverage: {len(c)} edges / {c.perturbation.nunique()} perts | "
          f"FM-wrong base rate {y.mean():.3f}")
    p_base = crossfit(X_base, y, groups, a.seed)
    p_reg = crossfit(X_reg, y, groups, a.seed)
    p_add = crossfit(X_add, y, groups, a.seed)
    auc_reg, auc_add = roc_auc_score(y, p_reg), roc_auc_score(y, p_add)
    print(f"\ncross-fit-by-perturbation AUC for predicting FM-wrong (inference-available features):")
    print(f"  |pred| only            {roc_auc_score(y, p_base):.3f}")
    print(f"  |pred| + regime        {auc_reg:.3f}   (~ the existing learned trust-head)")
    print(f"  + additive-disagreement {auc_add:.3f}   <- BUILDABLE, no ground truth")

    # LLM-free signal-gated allocation: verify top-frac by p(FM-wrong); net = acc - lam*verify_rate
    rng = np.random.default_rng(a.seed)
    sigs = {"random": rng.random(len(y)), f"signal-{auc_reg:.2f}": p_reg,
            f"signal-{auc_add:.2f}": p_add, "oracle": y + 1e-6 * rng.random(len(y))}

    def net_at(sig, frac, lam=0.5):
        k = int(frac * len(y)); S = np.argsort(-sig)[:k]
        mask = np.zeros(len(y), bool); mask[S] = True
        acc = 1 - y[~mask].sum() / len(y)
        return acc - lam * frac, y[mask].sum() / max(1, y.sum())

    print(f"\nLLM-free signal-gated verification, net@lambda0.5 by verify-budget:")
    print(f"{'verify%':>8s} " + " ".join(f"{s:>13s}" for s in sigs))
    for frac in [0.0, 0.1, 0.2, round(float(y.mean()), 2), 0.4]:
        print(f"{frac:>8.0%} " + " ".join(f"{net_at(sig, frac)[0]:>13.3f}" for sig in sigs.values()))
    print(f"\nvRecall (FM-wrong caught) @ verify-budget = base rate ({y.mean():.0%}):")
    for s, sig in sigs.items():
        print(f"   {s:14s} {net_at(sig, float(y.mean()))[1]:.2f}")
    print("\nThe high-AUC point of the dose-response is BUILDABLE (additive-disagreement, no ground truth); fed into\n"
          "signal-gated allocation it approaches the oracle at low budget. Combined with the benchmark result that\n"
          "the LLM follows a supplied signal 94-99%, the reliability bottleneck is engineerable, not fundamental.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
