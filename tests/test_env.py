"""Environment tests with a mocked LLM (no API calls) + the equivalence tool."""
import types

from verify_or_trust.env import run_episode
from verify_or_trust.panels import PanelConfig, build_panels
from verify_or_trust.tools import equivalence_test


def _tu(name, inp, i="t"):
    return types.SimpleNamespace(type="tool_use", id=i, name=name, input=inp)


class _FakeMessages:
    """Turn 1: assay two genes via run_de. Turn 2: submit a call for every gene."""
    def __init__(self, panel):
        self.panel = panel
        self.turn = 0

    def create(self, **kw):
        self.turn += 1
        genes = [g["gene"] for g in self.panel["panel"]]
        if self.turn == 1:
            return types.SimpleNamespace(content=[_tu("run_de", {"genes": genes[:2]}, "a")],
                                         stop_reason="tool_use")
        calls = [{"gene": g, "call": "no_effect", "confidence": 0.5} for g in genes]
        return types.SimpleNamespace(content=[_tu("submit", {"calls": calls}, "b")], stop_reason="tool_use")


class _FakeClient:
    def __init__(self, panel):
        self.messages = _FakeMessages(panel)


def test_run_episode_dry(make_substrate):
    panels = build_panels(make_substrate(), PanelConfig(N=20, min_wrong=3, min_correct=3, seed=1))
    p = panels[0]
    rec = run_episode(_FakeClient(p), "fake-model", p, lam=0.5)
    assert rec["submitted_n"] == p["n_panel"]
    assert set(rec["calls"]) == {g["gene"] for g in p["panel"]}
    assert rec["n_de"] == 2                       # assayed exactly the two genes from turn 1
    assert rec["n_turns"] == 2


def test_equivalence_tool():
    assert equivalence_test(0.0, 0.01) == "TESTED_NEGATIVE"
    assert equivalence_test(2.0, 0.01) == "POSITIVE"
    assert equivalence_test(0.2, 0.5) == "UNTESTED"
