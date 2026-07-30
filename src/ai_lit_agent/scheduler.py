from __future__ import annotations

import argparse
import os
import sys

from ai_lit_agent.ai_client import OpenAICompatibleClient
from ai_lit_agent.ai_settings import load_ai_settings
from ai_lit_agent.notifications import send_briefing_email
from ai_lit_agent.providers import PubMedProvider
from ai_lit_agent.research_agent import ResearchAgent
from ai_lit_agent.storage import PaperStore
from ai_lit_agent.summarizer import ExtractiveSummarizer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lit-agent-run-due",
        description="Run due Research Briefings and store the results.",
    )
    parser.add_argument(
        "--db",
        default=os.environ.get("AI_LIT_AGENT_DB", "data/literature.db"),
        help="Path to the literature SQLite database.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all saved briefings instead of only scheduled briefings that are due.",
    )
    parser.add_argument(
        "--email",
        action="store_true",
        help="Send an email summary when SMTP environment variables are configured.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    store = PaperStore(args.db)
    settings = load_ai_settings()
    ai_client = OpenAICompatibleClient(settings) if settings.configured else None
    agent = ResearchAgent(store, PubMedProvider(), ExtractiveSummarizer(), ai_client=ai_client)
    try:
        result = agent.run_watch_searches(due_only=not args.all)
    except OSError as error:
        print(f"Could not complete scheduled briefing run: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    print(result.brief)
    print("")
    print(f"Stored briefing run: {result.run_id}")

    if args.email:
        sent = send_briefing_email("AI Literature Agent Research Briefing", result.brief)
        print("Email sent." if sent else "Email not sent; SMTP environment variables are not configured.")


if __name__ == "__main__":
    main()
