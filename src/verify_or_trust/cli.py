"""Command-line entry point: `vot <command> ...`.

  vot panels     build evaluation panels from a substrate table
  vot baselines  run the LLM-free baseline policies (the K1 value proof)   [wired in release step 4]
  vot grade      grade episode outputs                                     [wired in release step 5]
  vot run        run the agentic environment with an LLM (`agent` extra)   [wired in release step 6]
"""
from __future__ import annotations

import argparse
import sys

from .panels import PanelConfig, build_panels, write_panels


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

    for name in ("baselines", "grade", "run"):
        sub.add_parser(name, help=f"{name} (wired in a later release step)")

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
