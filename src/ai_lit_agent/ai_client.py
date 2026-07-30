from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from ai_lit_agent.ai_settings import AISettings, normalize_provider
from ai_lit_agent.models import Paper
from ai_lit_agent.storage import SavedSearch


@dataclass(frozen=True)
class AIResult:
    text: str
    used: bool
    error: str = ""


@dataclass(frozen=True)
class AIPaperContext:
    paper: Paper
    full_text: str = ""


class LiteratureAIClient:
    def __init__(self, settings: AISettings, timeout: int = 45) -> None:
        self.settings = settings
        self.timeout = timeout

    def improve_research_brief(
        self,
        base_brief: str,
        searches: list[SavedSearch],
        papers: list[Paper],
        paper_contexts: list[AIPaperContext] | None = None,
    ) -> AIResult:
        if not self.settings.configured:
            return AIResult(text=base_brief, used=False)

        contexts = paper_contexts or [AIPaperContext(paper) for paper in papers]
        prompt = _brief_prompt(base_brief, searches, contexts)
        if normalize_provider(self.settings.provider) == "anthropic":
            return self._anthropic_message(base_brief, prompt)
        return self._openai_compatible_message(base_brief, prompt)

    def _openai_compatible_message(self, base_brief: str, prompt: str) -> AIResult:
        payload = {
            "model": self.settings.model,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You help researchers review literature search results. "
                        "Be concise, cautious, and clear about what is based only on titles and abstracts."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }
        request = urllib.request.Request(
            f"{self.settings.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.settings.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            return AIResult(text=base_brief, used=False, error=str(error))

        try:
            content = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError, AttributeError):
            return AIResult(text=base_brief, used=False, error="The AI provider returned an unexpected response.")
        if not content:
            return AIResult(text=base_brief, used=False, error="The AI provider returned an empty response.")
        return AIResult(text=content, used=True)

    def _anthropic_message(self, base_brief: str, prompt: str) -> AIResult:
        payload = {
            "model": self.settings.model,
            "max_tokens": 1800,
            "temperature": 0.2,
            "system": (
                "You help researchers review literature search results. "
                "Be concise, cautious, and clear about what is based only on titles and abstracts."
            ),
            "messages": [{"role": "user", "content": prompt}],
        }
        request = urllib.request.Request(
            f"{self.settings.base_url.rstrip('/')}/v1/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-api-key": self.settings.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            return AIResult(text=base_brief, used=False, error=str(error))

        try:
            content_blocks = data["content"]
            content = "\n".join(block.get("text", "") for block in content_blocks if block.get("type") == "text").strip()
        except (KeyError, TypeError, AttributeError):
            return AIResult(text=base_brief, used=False, error="The AI provider returned an unexpected response.")
        if not content:
            return AIResult(text=base_brief, used=False, error="The AI provider returned an empty response.")
        return AIResult(text=content, used=True)


OpenAICompatibleClient = LiteratureAIClient


def _brief_prompt(base_brief: str, searches: list[SavedSearch], paper_contexts: list[AIPaperContext]) -> str:
    search_names = ", ".join(search.name for search in searches) or "No saved briefing"
    paper_summaries = "\n\n".join(_paper_context(context) for context in paper_contexts[:20]) or "No candidate papers were found."
    return f"""Create a polished research briefing for: {search_names}

Use the candidate paper metadata below. Do not invent findings beyond the title and abstract. Keep the same practical structure:
- Search summary
- Read first
- Newest papers
- Leading themes
- Suggested next steps

Existing non-AI briefing:
{base_brief}

Candidate paper metadata:
{paper_summaries}
"""


def _paper_context(context: AIPaperContext) -> str:
    paper = context.paper
    authors = "; ".join(paper.authors) or "Unknown authors"
    abstract = (paper.abstract or "No abstract available.").replace("\n", " ")
    if len(abstract) > 1200:
        abstract = f"{abstract[:1200].rstrip()}..."
    full_text = context.full_text.replace("\n", " ").strip()
    if len(full_text) > 12000:
        full_text = f"{full_text[:12000].rstrip()}..."
    full_text_line = f"\nSaved PDF/full text excerpt: {full_text}" if full_text else ""
    return (
        f"Title: {paper.title}\n"
        f"Authors: {authors}\n"
        f"Year: {paper.year or 'n.d.'}\n"
        f"Type: {paper.paper_type or 'Other'}\n"
        f"Source: {paper.source}\n"
        f"DOI: {paper.doi or 'None'}\n"
        f"Abstract: {abstract}"
        f"{full_text_line}"
    )
