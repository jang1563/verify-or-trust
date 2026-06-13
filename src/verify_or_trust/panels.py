"""Build stratified per-perturbation evaluation panels.

A *panel* is one perturbation plus a candidate readout gene set, stratified to mix genes where the foundation
model (FM) is CORRECT (verifying them wastes budget) with genes where it is WRONG (the high-value verifications),
so that a good verification-allocation strategy measurably beats random/brute-force.

Input: a substrate table with one row per (perturbation, gene) edge and columns
  perturbation, gene, fm_log2FC, fm_call (effect|no_effect), real_label (POSITIVE|TESTED_NEGATIVE), regime,
  and the raw measured stats for the verify tool: raw_log2FC, raw_se, raw_q, n_trt, n_cntrl.
(Substrate builders in `verify_or_trust.substrates` produce this table from source.)
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

__all__ = ["PanelConfig", "build_panels", "write_panels"]

# raw-stat columns carried to each gene so the run_de tool can return measured values
_RAW_COLS = ["raw_log2FC", "raw_se", "raw_q", "n_trt", "n_cntrl"]


@dataclass
class PanelConfig:
    N: int = 30                 # target panel size
    min_wrong: int = 5          # min FM-wrong genes to include a perturbation
    min_correct: int = 5        # min FM-correct genes to include a perturbation
    seed: int = 13


def _stratum(fm_correct: bool, fm_call: str, real_call: str) -> str:
    if fm_correct:
        return "correct_effect" if real_call == "effect" else "correct_noeffect"
    return "wrong_FN" if fm_call == "no_effect" else "wrong_FP"  # FN: FM missed; FP: FM hallucinated


def build_panels(substrate: "pd.DataFrame | str", cfg: PanelConfig | None = None) -> list[dict]:
    """Build stratified panels from a substrate table (DataFrame or CSV path)."""
    cfg = cfg or PanelConfig()
    df = pd.read_csv(substrate) if isinstance(substrate, str) else substrate.copy()
    df = df.drop_duplicates()                 # one row per edge — guards any substrate against exact-duplicate rows
    rng = np.random.default_rng(cfg.seed)

    df = df[df["real_label"].isin(["POSITIVE", "TESTED_NEGATIVE"])].copy()
    df["real_call"] = np.where(df["real_label"] == "POSITIVE", "effect", "no_effect")
    df["fm_correct"] = df["fm_call"].values == df["real_call"].values
    df["stratum"] = [
        _stratum(c, fc, rc) for c, fc, rc in zip(df["fm_correct"], df["fm_call"], df["real_call"])
    ]

    counts = df.groupby("perturbation")["stratum"].value_counts().unstack(fill_value=0)
    for c in ["correct_effect", "correct_noeffect", "wrong_FN", "wrong_FP"]:
        if c not in counts:
            counts[c] = 0
    counts["n_wrong"] = counts[["wrong_FN", "wrong_FP"]].sum(1)
    counts["n_correct"] = counts[["correct_effect", "correct_noeffect"]].sum(1)
    eligible = set(counts[(counts.n_wrong >= cfg.min_wrong) & (counts.n_correct >= cfg.min_correct)].index)

    half = cfg.N // 2
    cols = ["gene", "fm_log2FC", "fm_call", "real_call", "fm_correct", "stratum", "regime", *_RAW_COLS]
    panels: list[dict] = []
    # iterate via a single groupby (O(n) total) rather than re-filtering per perturbation (O(n*perts) -- pathological
    # on large substrates). sorted=True preserves the perturbation order, so the seeded rng sequence is unchanged.
    for pert, sub in df.groupby("perturbation", sort=True):
        if pert not in eligible:
            continue

        def take(strata, k, _sub=sub):
            pool = _sub[_sub.stratum.isin(strata)]
            k = min(k, len(pool))
            return pool.iloc[rng.permutation(len(pool))[:k]]

        wrong = take(["wrong_FN", "wrong_FP"], half)
        correct = take(["correct_effect", "correct_noeffect"], cfg.N - len(wrong))
        panel = pd.concat([wrong, correct])
        panel = panel.iloc[rng.permutation(len(panel))]
        recs = [
            {
                k: (float(r[k]) if k in ("fm_log2FC", "raw_log2FC", "raw_se", "raw_q")
                    else bool(r[k]) if k == "fm_correct"
                    else int(r[k]) if k in ("n_trt", "n_cntrl")
                    else str(r[k]))
                for k in cols
            }
            for _, r in panel.iterrows()
        ]
        panels.append({"perturbation": str(pert), "n_panel": len(recs),
                       "n_wrong": int((panel.fm_correct == False).sum()), "panel": recs})  # noqa: E712
    return panels


def write_panels(panels: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        for rec in panels:
            f.write(json.dumps(rec) + "\n")
