"""GEARS / Norman 2019 substrate (public data).

The ready-to-use substrate table **ships in the repo** at `data/substrates/gears_norman.csv` (and on the Hugging
Face dataset) — `vot panels --substrate-table data/substrates/gears_norman.csv` runs immediately, no build needed.

`build_substrate` below is the from-scratch regeneration path. It is intentionally heavy and NOT run in CI: it
requires training GEARS (GPU, ~1h) and computing the sceptre ground-truth labels (R / the sceptre pipeline). The
steps are:
  1. Load Norman 2019 via GEARS (`PertData(...).load("norman")`; public, GEO GSE133344).
  2. Train GEARS (`model.train(epochs=20)`) and derive the predicted per-(perturbation, gene) effect:
     fm_log2FC = log2((pred_mean + eps) / (ctrl_mean + eps)); fm_call at |fm_log2FC| >= delta.
  3. Compute the held-out sceptre three-state label (POSITIVE / TESTED_NEGATIVE) + raw stats per edge.
  4. Join and emit the table in `SCHEMA.md` shape.
A faithful reference implementation of steps 1-2 is `eval/06_gears_norman.py` in the research repository; the
sceptre labeling is the standard sceptre marginal-effect pipeline. Most users should use the shipped table.
"""
from __future__ import annotations

__all__ = ["build_substrate"]

_SHIPPED = "data/substrates/gears_norman.csv"


def build_substrate(*args, **kwargs):
    raise NotImplementedError(
        "The GEARS/Norman substrate ships ready-to-use at "
        f"'{_SHIPPED}' (also on the Hugging Face dataset) -- use it directly:\n"
        f"    vot panels --substrate-table {_SHIPPED}\n"
        "Regenerating from scratch is a heavy GPU pipeline (train GEARS + compute sceptre labels); see this "
        "module's docstring and eval/06_gears_norman.py in the research repository."
    )
