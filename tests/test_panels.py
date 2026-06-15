"""Panel builder tests on a synthetic substrate (deterministic, no downloads)."""
import json

import numpy as np

from verify_or_trust.panels import PanelConfig, build_panels


def _reject_constant(value):
    raise ValueError(f"non-standard JSON constant: {value}")


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


def test_write_panels_creates_parent_dir(make_substrate, tmp_path):
    from verify_or_trust.panels import write_panels
    panels = build_panels(make_substrate(), PanelConfig(seed=1))
    out = tmp_path / "nested" / "deep" / "panels.jsonl"     # parent dirs do not exist
    write_panels(panels, str(out))
    assert out.exists() and out.read_text().count("\n") == len(panels)


def test_write_panels_uses_strict_json_null_for_missing_floats(make_substrate, tmp_path):
    from verify_or_trust.panels import write_panels
    sub = make_substrate(n_pert=4, n_gene=40, seed=5)
    sub["fm_log2FC"] = np.nan
    panels = build_panels(sub, PanelConfig(N=20, min_wrong=3, min_correct=3, seed=1))
    assert any(g["fm_log2FC"] is None for p in panels for g in p["panel"])

    out = tmp_path / "panels.jsonl"
    write_panels(panels, str(out))
    text = out.read_text()
    assert "NaN" not in text
    assert "null" in text
    for line in text.splitlines():
        json.loads(line, parse_constant=_reject_constant)
