"""Panel builder tests on a synthetic substrate (deterministic, no downloads)."""
from verify_or_trust.panels import PanelConfig, build_panels


def test_build_panels_structure(make_substrate):
    panels = build_panels(make_substrate(), PanelConfig(N=20, min_wrong=3, min_correct=3, seed=1))
    assert panels
    for p in panels:
        assert p["n_panel"] <= 20
        assert p["n_wrong"] >= 3
        genes = {g["gene"] for g in p["panel"]}
        assert len(genes) == p["n_panel"]
        for g in p["panel"]:
            assert {"raw_log2FC", "raw_se", "raw_q", "fm_call", "real_call"} <= set(g)


def test_build_panels_deterministic(make_substrate):
    sub = make_substrate()
    assert build_panels(sub, PanelConfig(seed=7)) == build_panels(sub, PanelConfig(seed=7))
