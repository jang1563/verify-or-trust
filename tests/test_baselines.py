"""Baseline / K1 tests on synthetic panels (deterministic)."""
from verify_or_trust.baselines import run_baselines
from verify_or_trust.panels import PanelConfig, build_panels


def _panels(make_substrate):
    return build_panels(make_substrate(n_pert=6, n_gene=40, seed=2),
                        PanelConfig(N=20, min_wrong=3, min_correct=3, seed=1))


def test_oracle_beats_baselines(make_substrate):
    pol = run_baselines(_panels(make_substrate), lam=0.5, seed=0)["policies"]
    assert pol["oracle"]["accuracy"] == 1.0
    assert pol["oracle"]["net"] > pol["trust-all"]["net"]
    assert pol["oracle"]["net"] > pol["brute-force"]["net"]


def test_k1_deterministic(make_substrate):
    a = run_baselines(_panels(make_substrate), seed=0)["k1"]
    b = run_baselines(_panels(make_substrate), seed=0)["k1"]
    assert a == b and "passed" in a
