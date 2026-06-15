"""Arc STATE / Tahoe substrate (real Arc foundation model; NON-COMMERCIAL license).

Downloads Arc Institute's pretrained ST-HVG-Tahoe released predictions (`*_pred_de.csv`) and the matched real
differential expression (`*_real_de.csv`) from the Arc Hugging Face repo, derives the STATE per-(perturbation,
gene) effect call, and emits a substrate table in the `SCHEMA.md` shape.

IMPORTANT: Arc's model and released data are under a non-commercial Model License + Acceptable Use Policy. This
builder downloads them only when invoked locally and does NOT redistribute them; by using it you accept Arc's terms.
Gene identities in the Tahoe release are integer feature indices (not symbols), so the `query_gene` knowledge tool
is unavailable for this substrate (and `run_de` here is the released DE, not live cells).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["build_substrate"]

_REPO = "arcinstitute/ST-HVG-Tahoe"
_DEFAULT_LINES = ["C32", "HOP62", "HepG2-C3A", "PANC-1"]  # 'Hs 766T' omitted (space in filename)


def _eval_dir(split: str) -> str:
    if split == "zeroshot":
        return "zeroshot/state_generalization_zeroshot_X_hvg/eval_best.ckpt"
    if split == "fewshot":
        return "fewshot/state_generalization_X_hvg/eval_best.ckpt"
    raise ValueError("split must be 'zeroshot' or 'fewshot'")


def build_substrate(cell_lines: list[str] | None = None, *, split: str = "zeroshot", delta: float = 0.25,
                    out: str | None = None, cache_dir: str | None = None) -> pd.DataFrame:
    """Download Arc ST-HVG-Tahoe pred/real DE and build the substrate table (you accept Arc's non-commercial terms)."""
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as e:  # pragma: no cover
        raise ImportError("install huggingface_hub to build the Tahoe substrate: pip install huggingface_hub") from e

    lines = cell_lines or _DEFAULT_LINES
    edir = _eval_dir(split)
    frames = []
    for line in lines:
        pf = hf_hub_download(_REPO, f"{edir}/{line}_pred_de.csv", cache_dir=cache_dir)
        rf = hf_hub_download(_REPO, f"{edir}/{line}_real_de.csv", cache_dir=cache_dir)
        cols = ["target", "feature", "fold_change", "fdr"]
        p = pd.read_csv(pf)[cols].rename(columns={"fold_change": "p_fc", "fdr": "p_fdr"})
        r = pd.read_csv(rf)[cols].rename(columns={"fold_change": "r_fc", "fdr": "r_fdr"})
        d = p.merge(r, on=["target", "feature"])
        d["cell_line"] = line
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)

    d["fm_log2FC"] = np.log2(d["p_fc"].clip(lower=1e-6))
    real_log2FC = np.log2(d["r_fc"].clip(lower=1e-6))
    # STATE call = predicted-significant & sizeable (matched to the real criterion); real call likewise
    d["fm_call"] = np.where((d["p_fdr"] < 0.05) & (d["fm_log2FC"].abs() >= delta), "effect", "no_effect")
    real_call = np.where((d["r_fdr"] < 0.05) & (real_log2FC.abs() >= delta), "effect", "no_effect")
    d["real_label"] = np.where(real_call == "effect", "POSITIVE", "TESTED_NEGATIVE")
    drug = d["target"].str.extract(r"\('([^']+)'", expand=False).fillna(d["target"])
    dose = d["target"].str.extract(r",\s*([0-9.]+)", expand=False).fillna("0")
    d["perturbation"] = drug + "@" + dose + "|" + d["cell_line"]
    d["gene"] = "g" + d["feature"].astype(str)
    d["regime"] = d["cell_line"]
    d["raw_log2FC"] = real_log2FC
    d["raw_q"] = d["r_fdr"]
    # a usable SE proxy from the q-value (the release does not expose SE)
    d["raw_se"] = (real_log2FC.abs() / np.maximum(0.1, (-np.log10(d["r_fdr"].clip(1e-300, 1))).clip(lower=0.01))
                   ).clip(0.01, 5.0)
    d["n_trt"] = 0
    d["n_cntrl"] = 0

    cols = ["perturbation", "gene", "fm_log2FC", "fm_call", "real_label", "regime",
            "raw_log2FC", "raw_se", "raw_q", "n_trt", "n_cntrl"]
    out_df = d[cols]
    if out:
        import os
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        out_df.to_csv(out, index=False)
    return out_df
