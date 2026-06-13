"""The agentic verification-allocation environment.

A multi-turn tool-use loop: the agent sees a perturbation + a readout panel with the foundation model's (FM)
predictions, decides which genes to verify with the costly `run_de` tool, may look up gene function (`query_gene`)
or run an `equivalence_test`, and submits a call for every gene. Reward = correct calls - lambda * assays.

Model-agnostic: pass any object exposing `.messages.create(model, max_tokens, system, messages, tools)` with the
Anthropic Messages API shape (the `anthropic` SDK, or a fake for testing). The API key is the SDK's concern
(read from ANTHROPIC_API_KEY); this module never touches keys.

An optional per-gene reliability signal (`reliability_flags`: {gene: is_unreliable}) can be supplied — e.g. from a
learned trust head — to study deployable calibrated orchestration. (This module does not fabricate signals from
ground truth; that is a research-only probe kept out of the public benchmark.)
"""
from __future__ import annotations

import json

from .tools import DELTA, GeneDB, LiveDE, equivalence_test

__all__ = ["SYSTEM", "tools_spec", "run_episode"]

SYSTEM = """You are a computational biologist analyzing a CRISPRa perturbation experiment. A fast foundation-model
predictor has estimated, for each gene in a readout panel, the perturbation's effect (predicted log2 fold-change).
The predictor is good but not perfect -- it is sometimes confidently wrong. For EVERY gene decide whether the
perturbation changes its expression (effect_up / effect_down), does NOT (no_effect), or is undetermined (untested).

You may run the real differential-expression assay on specific genes for the ground-truth measurement, but it
COSTS you. Scoring: +1 per correct final call, -{LAM} per gene assayed. Maximize your NET score -- verify only
where checking is worth the cost, and trust the predictor where it is likely right. A rigorous 'no_effect' should
be supported by an equivalence test, not merely a non-significant result. When finished, call submit with a call
for every gene. Return tool calls only; no prose."""


def tools_spec(with_query: bool = False) -> list[dict]:
    ts = [
        {"name": "run_de", "description": "Run the real differential-expression assay on one or more genes. "
         "Returns measured log2FC, standard error, q-value, cell counts. COSTS lambda per gene.",
         "input_schema": {"type": "object", "properties": {"genes": {"type": "array",
            "items": {"type": "string"}, "description": "gene symbols to assay"}}, "required": ["genes"]}},
        {"name": "equivalence_test", "description": "TOST: is an effect of size >= delta excluded? Returns "
         "POSITIVE / TESTED_NEGATIVE / UNTESTED.",
         "input_schema": {"type": "object", "properties": {"log2fc": {"type": "number"}, "se": {"type": "number"},
            "delta": {"type": "number"}}, "required": ["log2fc", "se"]}},
        {"name": "submit", "description": "Submit final calls for ALL panel genes and end the episode.",
         "input_schema": {"type": "object", "properties": {"calls": {"type": "array", "items": {"type": "object",
            "properties": {"gene": {"type": "string"},
                "call": {"type": "string", "enum": ["effect_up", "effect_down", "no_effect", "untested"]},
                "confidence": {"type": "number"}}, "required": ["gene", "call"]}}}, "required": ["calls"]}},
    ]
    if with_query:
        ts.insert(2, {"name": "query_gene", "description": "Look up a gene's function / pathway / GO biological "
            "process from a biological database (NCBI/Ensembl/UniProt aggregate). FREE.",
            "input_schema": {"type": "object", "properties": {"gene": {"type": "string"}}, "required": ["gene"]}})
    return ts


def _build_prompt(panel: dict, lam: float, reliability_flags: dict | None) -> str:
    genes = panel["panel"]
    lines = [f"Perturbation: {panel['perturbation']} (CRISPRa). Readout panel ({len(genes)} genes). "
             "Foundation-model predictions (predicted log2FC; call at |log2FC|>=0.25):"]
    for g in genes:
        tag = ""
        if reliability_flags is not None:
            tag = ("  [FM-reliability: UNRELIABLE here]" if reliability_flags.get(g["gene"])
                   else "  [FM-reliability: reliable]")
        verdict = "EFFECT" if g["fm_call"] == "effect" else "no effect"
        lines.append(f"  {g['gene']}: pred_log2FC={g['fm_log2FC']:+.2f} -> FM says {verdict}{tag}")
    note = (" Each gene is annotated with the FM's per-gene reliability (informative but imperfect); use it to "
            "decide where assaying is worth the cost." if reliability_flags is not None else "")
    return ("\n".join(lines) + f"\n\nDecide which genes to assay (cost {lam}/gene), then submit a call for all "
            f"{len(genes)} genes. Maximize net score (+1 correct, -{lam}/assay).{note}")


def run_episode(client, model: str, panel: dict, lam: float = 0.5, *, live_de: "LiveDE | None" = None,
                genedb: "GeneDB | None" = None, reliability_flags: dict | None = None,
                max_turns: int = 12, max_tokens: int = 3000) -> dict:
    """Run one episode and return a record (calls, verified genes, queried genes, turn count)."""
    genes = {g["gene"]: g for g in panel["panel"]}
    user = _build_prompt(panel, lam, reliability_flags)
    msgs = [{"role": "user", "content": user}]
    verified: set[str] = set()
    queried: set[str] = set()
    submitted = None
    nturns = 0
    system = SYSTEM.replace("{LAM}", str(lam))

    for _ in range(max_turns):
        nturns += 1
        resp = client.messages.create(model=model, max_tokens=max_tokens, system=system, messages=msgs,
                                      tools=tools_spec(with_query=genedb is not None))
        msgs.append({"role": "assistant", "content": resp.content})
        tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
        if not tool_uses:
            msgs.append({"role": "user", "content": "Continue: assay genes if useful, then submit for all genes."})
            continue
        results = []
        for b in tool_uses:
            if b.name == "run_de":
                req = b.input.get("genes", [])
                inpanel = [gn for gn in req if gn in genes]
                live = live_de.run(panel["perturbation"], inpanel) if (live_de and inpanel) else None
                out = []
                for gn in req:
                    if gn not in genes:
                        out.append(f"{gn}: NOT in panel")
                        continue
                    verified.add(gn)
                    if live_de:
                        r = live[gn]
                        out.append(f"{gn}: {r['error']}" if "error" in r else
                                   f"{gn}: log2FC={r['log2FC']:+.3f}, SE={r['se']:.3f}, q={r['q']:.2g}, "
                                   f"n_trt={r['n_trt']}")
                    else:
                        g = genes[gn]
                        out.append(f"{gn}: log2FC={g['raw_log2FC']:+.3f}, SE={g['raw_se']:.3f}, "
                                   f"q={g['raw_q']:.2g}, n_trt={g['n_trt']}")
                results.append((b.id, "\n".join(out) or "no genes"))
            elif b.name == "equivalence_test":
                results.append((b.id, equivalence_test(float(b.input.get("log2fc", 0)),
                                                       float(b.input.get("se", 1)),
                                                       float(b.input.get("delta", DELTA)))))
            elif b.name == "query_gene":
                gn = b.input.get("gene", "")
                queried.add(gn)
                results.append((b.id, json.dumps(genedb.query(gn) if genedb else {"error": "unavailable"})))
            elif b.name == "submit":
                submitted = b.input.get("calls", [])
                results.append((b.id, "submitted"))
        msgs.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": i, "content": c}
                                                 for i, c in results]})
        if submitted is not None:
            break

    calls = {c.get("gene"): {"call": c.get("call"), "confidence": c.get("confidence")}
             for c in (submitted or []) if c.get("gene") in genes}
    return {"model": model, "perturbation": panel["perturbation"], "n_panel": len(genes),
            "n_wrong": panel.get("n_wrong"), "verified": sorted(verified), "n_de": len(verified),
            "queried": sorted(queried), "n_query": len(queried), "n_turns": nturns,
            "calls": calls, "submitted_n": len(submitted or [])}
