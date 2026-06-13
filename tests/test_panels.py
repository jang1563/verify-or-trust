"""Panel builder tests on a synthetic substrate (deterministic, no downloads)."""
import numpy as np
import pandas as pd

from verify_or_trust.panels import PanelConfig, build_panels


def _synthetic_substrate(n_pert=4, n_gene=40, seed=0):
    """A small substrate with a controlled mix of FM-correct and FM-wrong genes per perturbation."""
    rng = np.random.default_rng(seed)
    rows = []
    for p in range(n_pert):
        for g in range(n_gene):
            real_label = "POSITIVE" if rng.random() < 0.5 else "TESTED_NEGATIVE"
            real_eff = real_label == "POSITIVE"
            wrong = rng.random() < 0.4                    # ~40% FM-wrong
            fm_call = "no_effect" if (real_eff and wrong) or (not real_eff and not wrong) else "effect"
            rows.append(dict(perturbation=f"P{p}", gene=f"g{g}", fm_log2FC=float(rng.normal()),
                             fm_call=fm_call, real_label=real_label, regime="single",
                             raw_log2FC=float(rng.normal()), raw_se=0.1, raw_q=rng.random(),
                             n_trt=100, n_cntrl=200))
    return pd.DataFrame(rows)


def test_build_panels_structure():
    sub = _synthetic_substrate()
    panels = build_panels(sub, PanelConfig(N=20, min_wrong=3, min_correct=3, seed=1))
    assert panels, "no panels built"
    for p in panels:
        assert p["n_panel"] <= 20
        assert p["n_wrong"] >= 3
        genes = {g["gene"] for g in p["panel"]}
        assert len(genes) == p["n_panel"]                # no duplicate genes within a panel
        for g in p["panel"]:                             # every gene carries the verify-tool raw stats
            assert {"raw_log2FC", "raw_se", "raw_q", "fm_call", "real_call"} <= set(g)


def test_build_panels_deterministic():
    sub = _synthetic_substrate()
    a = build_panels(sub, PanelConfig(seed=7))
    b = build_panels(sub, PanelConfig(seed=7))
    assert a == b                                        # same seed -> identical panels
