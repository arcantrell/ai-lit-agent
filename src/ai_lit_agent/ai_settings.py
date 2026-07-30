from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AISettings:
    enabled: bool = False
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    input_mode: str = "abstracts_only"

    @property
    def configured(self) -> bool:
        return self.enabled and bool(self.api_key.strip()) and bool(self.model.strip())


def default_settings_path() -> Path:
    return Path(os.environ.get("AI_LIT_AGENT_AI_CONFIG", "data/ai_settings.json"))


def normalize_provider(value: str) -> str:
    provider = value.strip().lower()
    if provider in {"anthropic", "claude"}:
        return "anthropic"
    if provider in {"xai", "grok"}:
        return "xai"
    if provider in {"openai_compatible", "openai-compatible", "compatible"}:
        return "openai_compatible"
    return "openai"


def default_model(provider: str) -> str:
    normalized = normalize_provider(provider)
    if normalized == "anthropic":
        return "claude-haiku-4-5-20251001"
    if normalized == "xai":
        return "grok-4.3"
    return "gpt-4.1-mini"


def default_base_url(provider: str) -> str:
    normalized = normalize_provider(provider)
    if normalized == "anthropic":
        return "https://api.anthropic.com"
    if normalized == "xai":
        return "https://api.x.ai/v1"
    return "https://api.openai.com/v1"


def load_ai_settings(path: str | Path | None = None) -> AISettings:
    settings_path = Path(path) if path else default_settings_path()
    data: dict[str, object] = {}
    if settings_path.exists():
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}

    api_key = str(data.get("api_key") or "")
    provider = normalize_provider(str(data.get("provider") or "openai"))
    env_key = (
        os.environ.get("AI_LIT_AGENT_AI_KEY")
        or _provider_env_key(provider)
        or os.environ.get("OPENAI_API_KEY")
    )
    if env_key:
        api_key = env_key

    return AISettings(
        enabled=bool(data.get("enabled", False)),
        provider=provider,
        model=str(data.get("model") or default_model(provider)),
        base_url=str(data.get("base_url") or default_base_url(provider)),
        api_key=api_key,
        input_mode=normalize_input_mode(str(data.get("input_mode") or "abstracts_only")),
    )


def save_ai_settings(settings: AISettings, path: str | Path | None = None) -> AISettings:
    settings_path = Path(path) if path else default_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(
            {
                "enabled": settings.enabled,
                "provider": settings.provider,
                "model": settings.model,
                "base_url": settings.base_url.rstrip("/"),
                "api_key": settings.api_key,
                "input_mode": normalize_input_mode(settings.input_mode),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return load_ai_settings(settings_path)


def public_ai_settings(settings: AISettings) -> dict[str, object]:
    return {
        "enabled": settings.enabled,
        "provider": settings.provider,
        "model": settings.model,
        "base_url": settings.base_url,
        "has_api_key": bool(settings.api_key.strip()),
        "configured": settings.configured,
        "input_mode": normalize_input_mode(settings.input_mode),
    }


def normalize_input_mode(value: str) -> str:
    if value in {"candidate_full_pdfs", "all_candidate_pdfs", "all_full_text"}:
        return "candidate_full_pdfs"
    if value in {"saved_full_text", "full_text", "pdfs"}:
        return "saved_full_text"
    return "abstracts_only"


def _provider_env_key(provider: str) -> str | None:
    if provider == "anthropic":
        return os.environ.get("ANTHROPIC_API_KEY")
    if provider == "xai":
        return os.environ.get("XAI_API_KEY")
    return os.environ.get("OPENAI_API_KEY")
