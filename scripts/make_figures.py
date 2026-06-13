"""Generate the headline figure from the published research numbers (results/RESULTS.md).

    pip install matplotlib
    python scripts/make_figures.py        # -> results/capability_inversion.png

The values are the research-run results (Anthropic Haiku 4.5 / Sonnet 4.6 / Opus 4.8, GEARS/Norman, λ=0.5);
reproduce them with `vot run` + `vot grade`.
"""
import matplotlib.pyplot as plt
from matplotlib import font_manager  # noqa: F401  (ensures default fonts load)

OUT = "results/capability_inversion.png"

# GEARS/Norman, 110 panels, λ=0.5 (net reward = correct - λ*assays)
TRUST_ALL, ORACLE = 16.71, 21.60
MODELS = ["Haiku 4.5", "Sonnet 4.6", "Opus 4.8"]
NET = [14.34, 14.14, 13.35]
ASSAY = [41, 61, 76]
# Opus net under each condition: no signal / + domain knowledge / + learned signal / + ideal signal
COND = ["no signal", "+ gene\nknowledge", "+ learned\nsignal", "+ ideal\nsignal"]
COND_NET = [13.35, 13.19, 15.30, 17.03]
COND_COLOR = ["#b0b0b0", "#d98a8a", "#5b8def", "#2f6fd0"]

plt.rcParams.update({"font.size": 11})
fig, (axA, axB) = plt.subplots(1, 2, figsize=(11, 4.3))

# ---- Panel A: capability inversion ----
x = range(len(MODELS))
axA.axhspan(0, TRUST_ALL, color="#fbeaea", zorder=0)  # "worse than just trusting the FM" zone
axA.axhline(TRUST_ALL, color="#e07b39", ls="--", lw=1.4, label=f"trust-all (never verify) = {TRUST_ALL}")
axA.axhline(ORACLE, color="#2e8b57", ls="--", lw=1.4, label=f"oracle (verify iff FM wrong) = {ORACLE}")
axA.plot(x, NET, "-o", color="#c0392b", lw=2.2, ms=9, zorder=3)
for xi, (m, nt, a) in enumerate(zip(MODELS, NET, ASSAY)):
    axA.annotate(f"{nt:.1f}\n({a}% assayed)", (xi, nt), textcoords="offset points", xytext=(0, -28),
                 ha="center", fontsize=9, color="#333")
axA.annotate("more capable →\nover-verifies more →\nworse net", (1.0, 15.6), ha="center", fontsize=9.5,
             color="#c0392b", fontweight="bold")
axA.set_xticks(list(x))
axA.set_xticklabels(MODELS)
axA.set_ylabel("net reward  (correct − λ·assays)")
axA.set_ylim(12, 22.4)
axA.set_title("Capability inversion: the strongest model is the worst orchestrator", fontsize=11.5)
axA.legend(loc="upper center", fontsize=8.5, frameon=False)
axA.spines[["top", "right"]].set_visible(False)

# ---- Panel B: knowledge doesn't fix it, a reliability signal does ----
xb = range(len(COND))
axB.axhline(TRUST_ALL, color="#e07b39", ls="--", lw=1.4)
axB.bar(xb, COND_NET, color=COND_COLOR, width=0.62, zorder=3)
for xi, v in zip(xb, COND_NET):
    axB.annotate(f"{v:.1f}", (xi, v), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=9.5)
axB.annotate("trust-all", (3.35, TRUST_ALL), color="#e07b39", fontsize=8.5, va="center")
axB.set_xticks(list(xb))
axB.set_xticklabels(COND, fontsize=9.5)
axB.set_ylabel("Opus 4.8 net reward")
axB.set_ylim(12, 18.4)
axB.set_title("The fix is a reliability signal — not domain knowledge", fontsize=11.5)
axB.spines[["top", "right"]].set_visible(False)

fig.suptitle("Frontier LLMs do not allocate verification over a fallible biology foundation model",
             fontsize=12.5, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"wrote {OUT}")
