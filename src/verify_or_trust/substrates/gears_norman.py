"""GEARS / Norman 2019 substrate (public data).

Trains/loads GEARS (Roohani et al., Nat Biotech 2024; MIT) on the Norman 2019 CRISPRa dataset (public, GEO
GSE133344, shipped by the GEARS package), derives the predicted per-(perturbation, gene) effect call, and joins a
held-out sceptre ground-truth label. Outputs the substrate table consumed by `panels.build_panels`. Also exposes
the cells for the live `run_de` tool. Wired in release step 3.
"""
from __future__ import annotations

__all__ = ["build_substrate"]


def build_substrate(*args, **kwargs):
    raise NotImplementedError("build_substrate is wired in release step 3")
