from __future__ import annotations

import argparse
import sys

from ai_lit_agent.agent import LiteratureAgent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lit-agent",
        description="Compile and summarize literature for a research topic.",
    )
    parser.add_argument("query", help="Research topic or search query.")
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of papers to retrieve.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    agent = LiteratureAgent()
    try:
        print(agent.compile_brief(query=args.query, limit=args.limit))
    except OSError as error:
        print(f"Could not complete literature search: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
