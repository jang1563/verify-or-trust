"""Shared test fixtures."""
import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def make_substrate():
    """Factory for a small synthetic substrate with a controlled FM-correct/FM-wrong mix per perturbation."""
    def _make(n_pert=4, n_gene=40, seed=0):
        rng = np.random.default_rng(seed)
        rows = []
        for p in range(n_pert):
            for g in range(n_gene):
                real_label = "POSITIVE" if rng.random() < 0.5 else "TESTED_NEGATIVE"
                real_eff = real_label == "POSITIVE"
                wrong = rng.random() < 0.4
                fm_call = "no_effect" if (real_eff and wrong) or (not real_eff and not wrong) else "effect"
                rows.append(dict(perturbation=f"P{p}", gene=f"g{g}", fm_log2FC=float(rng.normal()),
                                 fm_call=fm_call, real_label=real_label, regime="single",
                                 raw_log2FC=float(rng.normal()), raw_se=0.1, raw_q=float(rng.random()),
                                 n_trt=100, n_cntrl=200))
        return pd.DataFrame(rows)
    return _make
