"""Grade agentic episodes against the panels.

For each model, reports: accuracy, assays/gene, net reward (correct - lambda*assays), verification
precision/recall (did the agent assay the genes the FM was actually wrong on?), the accuracy a *random* allocator
would reach at the model's own assay budget (model > random => real allocation skill), and the untested rate.
"""
from __future__ import annotations

import glob
import json

import numpy as np

__all__ = ["load_episodes", "grade_episodes"]

# agent call enum -> coarse effect/no_effect/untested for comparison with the panel's real_call
_MAP = {"effect_up": "effect", "effect_down": "effect", "no_effect": "no_effect", "untested": "untested"}


def load_episodes(patterns: list[str]) -> list[dict]:
    rows = []
    for pat in patterns:
        for f in glob.glob(pat):
            for line in open(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r.get("calls") is not None:
                    rows.append(r)
    return rows


def grade_episodes(panels: list[dict], episodes: list[dict], lam: float = 0.5) -> dict:
    pmap = {p["perturbation"]: {g["gene"]: g for g in p["panel"]} for p in panels}
    by_model: dict[str, list[dict]] = {}
    for r in episodes:
        by_model.setdefault(r.get("model", "unknown"), []).append(r)

    out = {}
    for model, rows in by_model.items():
        accs, des, nets, vps, vrs, unts, randb = [], [], [], [], [], [], []
        for r in rows:
            gs = pmap.get(r["perturbation"])
            if gs is None:
                continue
            n = len(gs); ver = set(r["verified"]); calls = r["calls"]
            nc = sum(1 for gn, g in gs.items() if _MAP.get((calls.get(gn) or {}).get("call")) == g["real_call"])
            nu = sum(1 for gn in gs if _MAP.get((calls.get(gn) or {}).get("call")) == "untested")
            accs.append(nc / n); des.append(len(ver) / n); nets.append(nc - lam * len(ver)); unts.append(nu / n)
            wrong = {gn for gn, g in gs.items() if not g["fm_correct"]}
            if ver:
                vps.append(len([x for x in ver if x in wrong]) / len(ver))
            if wrong:
                vrs.append(len([x for x in ver if x in wrong]) / len(wrong))
            nw, k = len(wrong), len(ver)
            randb.append((n - (nw - (k * nw / n if n else 0))) / n)  # expected acc of a random allocator @ budget k
        out[model] = dict(
            n=len(rows),
            accuracy=float(np.mean(accs)), assays_per_gene=float(np.mean(des)), net=float(np.mean(nets)),
            verify_precision=float(np.mean(vps)) if vps else 0.0,
            verify_recall=float(np.mean(vrs)) if vrs else 0.0,
            accuracy_random_at_budget=float(np.mean(randb)), untested=float(np.mean(unts)),
        )
    return out
