"""Grader tests on synthetic panels + a constructed oracle episode."""
from verify_or_trust.grade import grade_episodes
from verify_or_trust.panels import PanelConfig, build_panels


def test_oracle_episode_scores_perfect(make_substrate):
    panels = build_panels(make_substrate(n_pert=4, n_gene=40, seed=3),
                          PanelConfig(N=20, min_wrong=3, min_correct=3, seed=1))
    # construct an "oracle" agent: verify exactly the FM-wrong genes, call every gene's true label
    eps = []
    for p in panels:
        wrong = [g["gene"] for g in p["panel"] if not g["fm_correct"]]
        calls = {g["gene"]: {"call": "effect_up" if g["real_call"] == "effect" else "no_effect"}
                 for g in p["panel"]}
        eps.append({"model": "oracle", "perturbation": p["perturbation"],
                    "verified": wrong, "calls": calls})
    res = grade_episodes(panels, eps, lam=0.5)["oracle"]
    assert res["accuracy"] == 1.0                      # all calls correct
    assert res["verify_precision"] == 1.0              # only FM-wrong genes verified
    assert res["net"] > 0
