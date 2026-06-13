"""The agentic verification-allocation environment.

A multi-turn tool-use loop: the agent sees a perturbation + a readout panel with the FM's predictions, decides
which genes to verify (via the costly `run_de`), may look up gene function (`query_gene`), and submits a call for
every gene. Reward = correct calls - lambda * assays. Model-agnostic; the LLM backend is pluggable (Anthropic SDK
via the `agent` extra). Optionally a per-gene reliability signal can be supplied (the deployable-orchestration arm).

Wired in release step 6 (ports `p1_env`, with the negbiodb dependency removed and the API key read from the
ANTHROPIC_API_KEY environment variable).
"""
from __future__ import annotations

__all__ = ["run_episode"]


def run_episode(*args, **kwargs):
    raise NotImplementedError("run_episode is wired in release step 6")
