from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Paper:
    title: str
    authors: tuple[str, ...] = field(default_factory=tuple)
    year: int | None = None
    abstract: str | None = None
    doi: str | None = None
    url: str | None = None
    open_access_pdf_url: str | None = None
    source: str = "unknown"
    paper_type: str = "Other"
    relevance_score: float = 0.0

    @property
    def citation_label(self) -> str:
        author = self.authors[0] if self.authors else "Unknown author"
        year = self.year if self.year is not None else "n.d."
        return f"{author} ({year})"

    def with_score(self, score: float) -> "Paper":
        return Paper(
            title=self.title,
            authors=self.authors,
            year=self.year,
            abstract=self.abstract,
            doi=self.doi,
            url=self.url,
            open_access_pdf_url=self.open_access_pdf_url,
            source=self.source,
            paper_type=self.paper_type,
            relevance_score=score,
        )
