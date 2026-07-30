from __future__ import annotations

import re
from collections import Counter

from ai_lit_agent.models import Paper

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}


class ExtractiveSummarizer:
    def rank(self, papers: list[Paper], query: str) -> list[Paper]:
        query_terms = set(_tokenize(query))
        scored = [paper.with_score(_score_paper(paper, query_terms)) for paper in papers]
        return sorted(scored, key=lambda paper: paper.relevance_score, reverse=True)

    def brief(self, query: str, papers: list[Paper], max_papers: int = 8) -> str:
        ranked = self.rank(papers, query)[:max_papers]
        themes = _theme_terms(ranked)

        lines = [
            f"# Literature Brief: {query}",
            "",
            f"Found {len(papers)} candidate papers and highlighted {len(ranked)}.",
            "",
            "## Leading Themes",
        ]

        if themes:
            lines.extend(f"- {term}" for term, _ in themes)
        else:
            lines.append("- No strong recurring terms were available from the retrieved metadata.")

        lines.extend(["", "## Key Papers"])
        for index, paper in enumerate(ranked, start=1):
            lines.extend(_paper_section(index, paper))

        lines.extend(
            [
                "",
                "## Caveats",
                "- This brief is based on retrieved metadata and abstracts, not full-text review.",
                "- Crossref metadata can be incomplete, especially for abstracts and author records.",
                "- Treat this as a starting map before screening papers manually.",
            ]
        )
        return "\n".join(lines)


def _paper_section(index: int, paper: Paper) -> list[str]:
    authors = "; ".join(paper.authors[:3])
    if len(paper.authors) > 3:
        authors += "; et al."
    authors = authors or "Unknown authors"

    lines = [
        f"{index}. **{paper.title}**",
        f"   - Citation: {authors} ({paper.year or 'n.d.'})",
        f"   - Relevance score: {paper.relevance_score:.2f}",
    ]
    if paper.abstract:
        lines.append(f"   - Summary: {_best_sentence(paper.abstract)}")
    if paper.doi:
        lines.append(f"   - DOI: {paper.doi}")
    if paper.url:
        lines.append(f"   - URL: {paper.url}")
    return lines


def _score_paper(paper: Paper, query_terms: set[str]) -> float:
    title_terms = Counter(_tokenize(paper.title))
    abstract_terms = Counter(_tokenize(paper.abstract or ""))
    title_hits = sum(title_terms[term] for term in query_terms)
    abstract_hits = sum(abstract_terms[term] for term in query_terms)
    recency = max((paper.year or 1900) - 2000, 0) / 100
    return title_hits * 3 + abstract_hits + recency


def _best_sentence(text: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentence = max(sentences, key=lambda candidate: len(_tokenize(candidate)), default=text)
    return sentence.strip()


def _theme_terms(papers: list[Paper], limit: int = 8) -> list[tuple[str, int]]:
    words: list[str] = []
    for paper in papers:
        words.extend(_tokenize(f"{paper.title} {paper.abstract or ''}"))
    counts = Counter(words)
    return counts.most_common(limit)


def _tokenize(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z-]{2,}", text.lower())
        if token not in STOPWORDS
    ]
