"""Build stratified per-perturbation evaluation panels.

A *panel* is one perturbation plus a candidate readout gene set, stratified to mix genes where the foundation
model (FM) is CORRECT (verifying them wastes budget) with genes where it is WRONG (the high-value verifications),
so that a good verification-allocation strategy measurably beats random/brute-force.

Wired in release step 3 (ports the research `p1_make_panels`).
"""
from __future__ import annotations

# Placeholder for the step-2 skeleton; ported with full logic + a regeneration test in step 3.
__all__ = ["build_panels"]


def build_panels(*args, **kwargs):  # noqa: D401
    raise NotImplementedError("build_panels is wired in release step 3")
