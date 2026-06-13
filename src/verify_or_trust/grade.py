"""Grade agentic episodes.

Headline metrics: net reward (correct calls - lambda*assays), verification precision/recall (did the agent assay
the genes the FM was actually wrong on?), accuracy vs a random allocator at the same budget, and the capability
spectrum (trust-all <-> oracle). Wired in release step 5 (ports `p1_grade`).
"""
from __future__ import annotations

__all__ = ["grade_episodes"]


def grade_episodes(*args, **kwargs):
    raise NotImplementedError("grade_episodes is wired in release step 5")
