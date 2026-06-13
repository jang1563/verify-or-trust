"""Programmatic quickstart: build panels, run the LLM-free value proof, (optionally) one agent episode.

    python examples/quickstart.py
"""
from verify_or_trust.baselines import run_baselines
from verify_or_trust.panels import PanelConfig, build_panels

SUBSTRATE = "data/substrates/gears_norman.csv"

panels = build_panels(SUBSTRATE, PanelConfig(seed=13))
print(f"built {len(panels)} panels")

res = run_baselines(panels, lam=0.5)
k1 = res["k1"]
print(f"K1 value proof: oracle {k1['oracle_acc']:.1%} vs random {k1['random_acc']:.1%} "
      f"-> gap {k1['gap']:+.1%} -> {'PASS' if k1['passed'] else 'FAIL'}")
for name, m in res["policies"].items():
    print(f"  {name:12s} acc={m['accuracy']:.1%}  net={m['net']:.2f}")

# To run an agent episode (needs `pip install -e '.[agent]'` and ANTHROPIC_API_KEY):
#   import anthropic
#   from verify_or_trust.env import run_episode
#   from verify_or_trust.grade import grade_episodes
#   rec = run_episode(anthropic.Anthropic(), "claude-...", panels[0], lam=0.5)
#   print(grade_episodes(panels, [rec]))
