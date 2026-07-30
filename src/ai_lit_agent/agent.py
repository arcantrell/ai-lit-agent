from __future__ import annotations

from ai_lit_agent.providers import MultiSearchProvider, SearchProvider
from ai_lit_agent.summarizer import ExtractiveSummarizer


class LiteratureAgent:
    def __init__(
        self,
        provider: SearchProvider | None = None,
        summarizer: ExtractiveSummarizer | None = None,
    ) -> None:
        self.provider = provider or MultiSearchProvider()
        self.summarizer = summarizer or ExtractiveSummarizer()

    def compile_brief(self, query: str, limit: int = 10) -> str:
        papers = self.provider.search(query=query, limit=limit)
        return self.summarizer.brief(query=query, papers=papers, max_papers=limit)
