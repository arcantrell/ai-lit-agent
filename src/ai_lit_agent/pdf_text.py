from __future__ import annotations

from pathlib import Path
import re

from pypdf import PdfReader

DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)


def extract_pdf_text(path: str | Path, max_pages: int = 80) -> str:
    reader = PdfReader(str(path))
    chunks: list[str] = []
    for page in reader.pages[:max_pages]:
        text = page.extract_text() or ""
        cleaned = " ".join(text.split())
        if cleaned:
            chunks.append(cleaned)
    return "\n\n".join(chunks)


def excerpt(text: str, max_chars: int = 900) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_chars:
        return normalized
    return f"{normalized[:max_chars].rstrip()}..."


def find_doi(text: str) -> str | None:
    match = DOI_PATTERN.search(text)
    if not match:
        return None
    return match.group(0).rstrip(".,;)")
