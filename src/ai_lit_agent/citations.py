from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

from ai_lit_agent.storage import SavedPaper

PdfPathResolver = Callable[[SavedPaper], str | Path | None]


def to_bibtex(papers: list[SavedPaper], pdf_path_resolver: PdfPathResolver | None = None) -> str:
    return "\n\n".join(_paper_to_bibtex(paper, pdf_path_resolver) for paper in papers)


def to_ris(papers: list[SavedPaper]) -> str:
    return "\n".join(_paper_to_ris(paper) for paper in papers)


def _paper_to_bibtex(saved: SavedPaper, pdf_path_resolver: PdfPathResolver | None = None) -> str:
    paper = saved.paper
    key = _citation_key(saved)
    entry_type = "article" if paper.paper_type in {"Research", "Review", "Other"} else "misc"
    fields = {
        "title": paper.title,
        "author": " and ".join(_bibtex_author(author) for author in paper.authors),
        "year": str(paper.year) if paper.year else "",
        "doi": paper.doi or "",
        "url": paper.url or "",
        "abstract": paper.abstract or "",
        "keywords": ", ".join(saved.subjects),
        "file": _bibtex_file_field(saved, pdf_path_resolver),
        "note": saved.notes,
    }
    lines = [f"@{entry_type}{{{key},"]
    lines.extend(f"  {name} = {{{value}}}," for name, value in fields.items() if value)
    lines.append("}")
    return "\n".join(lines)


def _paper_to_ris(saved: SavedPaper) -> str:
    paper = saved.paper
    ty = "JOUR" if paper.paper_type != "Review" else "RPRT"
    lines = [f"TY  - {ty}", f"TI  - {paper.title}"]
    lines.extend(f"AU  - {author}" for author in paper.authors)
    if paper.year:
        lines.append(f"PY  - {paper.year}")
    if paper.doi:
        lines.append(f"DO  - {paper.doi}")
    if paper.url:
        lines.append(f"UR  - {paper.url}")
    if paper.abstract:
        lines.append(f"AB  - {paper.abstract}")
    lines.extend(f"KW  - {subject}" for subject in saved.subjects)
    if saved.notes:
        lines.append(f"N1  - {saved.notes}")
    lines.append("ER  -")
    return "\n".join(lines)


def _citation_key(saved: SavedPaper) -> str:
    author = saved.paper.authors[0].split(",")[0] if saved.paper.authors else "paper"
    year = saved.paper.year or "nd"
    title_word = next(iter(re.findall(r"[A-Za-z0-9]+", saved.paper.title)), "study")
    return re.sub(r"[^A-Za-z0-9_:-]", "", f"{author}{year}{title_word}")


def _bibtex_author(author: str) -> str:
    return author.replace("{", "").replace("}", "")


def _bibtex_file_field(saved: SavedPaper, pdf_path_resolver: PdfPathResolver | None = None) -> str:
    if pdf_path_resolver is None and not saved.pdf_path:
        return ""
    resolved_path = pdf_path_resolver(saved) if pdf_path_resolver else saved.pdf_path
    if not resolved_path:
        return ""
    path = str(resolved_path)
    if Path(path).is_absolute():
        path = str(Path(path).expanduser().resolve())
    path = path.replace("{", "").replace("}", "")
    return f":{path}:PDF"
