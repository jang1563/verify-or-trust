"""LLM-free baseline policies on the panels — the pre-registered value proof (K1).

Each policy chooses a verify-set; verified genes are answered correctly, unverified genes by the FM. The benchmark
is only meaningful if directed allocation (oracle / FM-magnitude) beats random/brute-force on accuracy-per-assay.

Policies: trust-all, brute-force, random-K, FM-magnitude, oracle. Wired in release step 4 (ports `p1_baselines`).
"""
from __future__ import annotations

__all__ = ["run_baselines"]


def run_baselines(*args, **kwargs):
    raise NotImplementedError("run_baselines is wired in release step 4")
