"""Command-line entry point: `vot <command> ...`.

  vot panels     build evaluation panels from a substrate table
  vot baselines  run the LLM-free baseline policies (the K1 value proof)   [wired in release step 4]
  vot grade      grade episode outputs                                     [wired in release step 5]
  vot run        run the agentic environment with an LLM (`agent` extra)   [wired in release step 6]
"""
from __future__ import annotations

import argparse
import json
import sys

from .baselines import load_panels, run_baselines
from .grade import grade_episodes, load_episodes
from .panels import PanelConfig, build_panels, write_panels


def _cmd_run(a: argparse.Namespace) -> int:
    import os
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("error: set ANTHROPIC_API_KEY in the environment.", file=sys.stderr)
        return 2
    try:
        import anthropic
    except ImportError:
        print("error: install the agent extra:  pip install -e '.[agent]'", file=sys.stderr)
        return 2
    from .env import run_episode
    from .tools import GeneDB, LiveDE

    panels = load_panels(a.panels)
    live_de = LiveDE(a.real_de) if a.real_de else None
    genedb = GeneDB(a.query_gene) if a.query_gene else None
    client = anthropic.Anthropic()  # key from ANTHROPIC_API_KEY
    import os
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w") as fh:
        for i, p in enumerate(panels, 1):
            rec = run_episode(client, a.model, p, lam=a.lam, live_de=live_de, genedb=genedb)
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            print(f"[vot] {i}/{len(panels)} {p['perturbation']} de={rec['n_de']} calls={rec['submitted_n']}",
                  file=sys.stderr)
    print(f"[vot] wrote {len(panels)} episodes -> {a.out}")
    return 0


def _cmd_grade(a: argparse.Namespace) -> int:
    res = grade_episodes(load_panels(a.panels), load_episodes(a.episodes), lam=a.lam)
    hdr = ("model", "n", "acc", "assay", "net", "vPrec", "vRecall", "rand@b", "untest")
    print("  " + " ".join(f"{h:>9s}" for h in hdr))
    for model, m in res.items():
        print(f"  {model.split('-')[1] if '-' in model else model:>9s} {m['n']:>9d} {m['accuracy']:>9.1%} "
              f"{m['assays_per_gene']:>9.0%} {m['net']:>9.2f} {m['verify_precision']:>9.0%} "
              f"{m['verify_recall']:>9.0%} {m['accuracy_random_at_budget']:>9.1%} {m['untested']:>9.0%}")
    return 0


def _cmd_baselines(a: argparse.Namespace) -> int:
    res = run_baselines(load_panels(a.panels), lam=a.lam)
    print(f"baselines on {res['n_panels']} panels (lambda={res['lam']})")
    print(f"  {'policy':12s} {'acc':>7s} {'assay/g':>8s} {'net':>7s}")
    for name, m in res["policies"].items():
        print(f"  {name:12s} {m['accuracy']:>7.1%} {m['assays_per_gene']:>8.0%} {m['net']:>7.2f}")
    k = res["k1"]
    print(f"  K1: oracle {k['oracle_acc']:.1%} vs random {k['random_acc']:.1%} at equal budget "
          f"-> gap {k['gap']:+.1%} -> {'PASS' if k['passed'] else 'FAIL'}")
    return 0 if k["passed"] else 1


def _cmd_panels(a: argparse.Namespace) -> int:
    if not a.substrate_table:
        print("error: --substrate-table <csv> is required (build it first with a substrate builder; the "
              "download+train substrate builders land in release step 3).", file=sys.stderr)
        return 2
    panels = build_panels(a.substrate_table, PanelConfig(N=a.N, min_wrong=a.min_wrong,
                                                         min_correct=a.min_correct, seed=a.seed))
    write_panels(panels, a.out)
    print(f"[vot] wrote {len(panels)} panels -> {a.out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vot", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("panels", help="build evaluation panels from a substrate table")
    p.add_argument("--substrate-table", help="CSV with one row per (perturbation, gene) edge (see panels.py)")
    p.add_argument("--out", default="panels.jsonl")
    p.add_argument("--N", type=int, default=30)
    p.add_argument("--min-wrong", type=int, default=5, dest="min_wrong")
    p.add_argument("--min-correct", type=int, default=5, dest="min_correct")
    p.add_argument("--seed", type=int, default=13)
    p.set_defaults(func=_cmd_panels)

    b = sub.add_parser("baselines", help="LLM-free baseline policies (the K1 value proof)")
    b.add_argument("--panels", required=True)
    b.add_argument("--lam", type=float, default=0.5)
    b.set_defaults(func=_cmd_baselines)

    gr = sub.add_parser("grade", help="grade episode outputs against the panels")
    gr.add_argument("--panels", required=True)
    gr.add_argument("--episodes", required=True, nargs="+", help="episode jsonl path(s) / glob(s)")
    gr.add_argument("--lam", type=float, default=0.5)
    gr.set_defaults(func=_cmd_grade)

    rn = sub.add_parser("run", help="run the agentic environment with an LLM (needs the 'agent' extra)")
    rn.add_argument("--panels", required=True)
    rn.add_argument("--model", required=True)
    rn.add_argument("--lam", type=float, default=0.5)
    rn.add_argument("--out", default="episodes.jsonl")
    rn.add_argument("--real-de", help="path to perturb-seq cells h5ad; run_de computes live DE on the cells")
    rn.add_argument("--query-gene", help="path to a gene-annotation cache json; enables the query_gene DB tool")
    rn.set_defaults(func=_cmd_run)

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    if hasattr(args, "func"):
        return args.func(args)
    print(f"[vot] '{args.command}' is not wired yet in this build.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
