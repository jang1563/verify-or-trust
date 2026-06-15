# Data schemas

Explicit shapes for every artifact, so humans *and* agents can produce/consume them without reading the source.

## Substrate table (CSV) — input to `vot panels`
One row per (perturbation, gene) edge. Columns:

| column | type | meaning |
|---|---|---|
| `perturbation` | str | perturbation id (e.g. `ETS2+IKZF3`; `X+ctrl` / `X` for singles) |
| `gene` | str | readout gene (symbol for `gears_norman`; index for `state_tahoe`) |
| `fm_log2FC` | float\|null | the foundation model's predicted log2 fold-change; `null` when the source prediction is missing |
| `fm_call` | `effect`\|`no_effect` | FM call (|fm_log2FC| ≥ δ) |
| `real_label` | `POSITIVE`\|`TESTED_NEGATIVE` | held-out ground truth (UNTESTED rows are dropped) |
| `regime` | str | reliability regime / novelty tag (substrate-specific) |
| `raw_log2FC`,`raw_se`,`raw_q` | float | measured stats returned by the `run_de` tool |
| `n_trt`,`n_cntrl` | int | cell counts |

`real_call` = `effect` iff `real_label == POSITIVE`. `fm_correct` = `fm_call == real_call` (derived).

## Panel (JSONL) — output of `vot panels`, input to `vot run` / `vot baselines` / `vot grade`
One JSON object per line = one perturbation's evaluation panel:
```json
{"perturbation": "ETS2+IKZF3", "n_panel": 30, "n_wrong": 11,
 "panel": [{"gene": "LYL1", "fm_log2FC": 0.00, "fm_call": "no_effect", "real_call": "effect",
            "fm_correct": false, "stratum": "wrong_FN", "regime": "combo_in_train",
            "raw_log2FC": 0.39, "raw_se": 0.046, "raw_q": 5.9e-16, "n_trt": 393, "n_cntrl": 10345}, ...]}
```
`stratum` ∈ {`correct_effect`, `correct_noeffect`, `wrong_FN` (FM missed), `wrong_FP` (FM hallucinated)}.

## Episode (JSONL) — output of `vot run`, input to `vot grade`
One JSON object per line = one agent episode:
```json
{"model": "...", "perturbation": "ETS2+IKZF3", "n_panel": 30, "n_wrong": 11,
 "verified": ["KLF1", ...], "n_de": 17, "queried": [...], "n_query": 0, "n_turns": 6,
 "calls": {"LYL1": {"call": "effect_up", "confidence": 0.8}, ...}, "submitted_n": 30}
```
`call` ∈ {`effect_up`, `effect_down`, `no_effect`, `untested`} → graded as `effect` / `effect` / `no_effect` /
`untested` against the panel's `real_call`.

## Programmatic API (alternative to the CLI)
```python
from verify_or_trust.panels import build_panels, PanelConfig, write_panels
from verify_or_trust.baselines import run_baselines
from verify_or_trust.grade import grade_episodes
from verify_or_trust.env import run_episode          # needs an Anthropic-shaped client

panels = build_panels("substrate.csv", PanelConfig(seed=13))
k1 = run_baselines(panels)["k1"]                      # {'passed': True, 'gap': 0.234, ...}
# rec = run_episode(client, model, panels[0], lam=0.5)   # one agent episode
# metrics = grade_episodes(panels, [rec])
```
All randomness is seeded; same seed → identical panels/baselines.
