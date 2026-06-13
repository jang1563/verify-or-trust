"""Command-line entry point: `vot <command> ...`.

Commands (wired incrementally — see the release plan):
  vot panels     build evaluation panels from a substrate
  vot baselines  run the LLM-free baseline policies (the K1 value proof)
  vot grade      grade episode outputs
  vot run        run the agentic environment with an LLM (requires the `agent` extra)
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vot", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("panels", help="build evaluation panels from a substrate")
    sub.add_parser("baselines", help="run LLM-free baseline policies (K1 value proof)")
    sub.add_parser("grade", help="grade episode outputs")
    sub.add_parser("run", help="run the agentic environment with an LLM")
    args, rest = parser.parse_known_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    # subcommands are wired in their respective modules in later release steps.
    print(f"[vot] '{args.command}' is not wired yet in this build.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
