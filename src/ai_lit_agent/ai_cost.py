from __future__ import annotations

from dataclasses import dataclass

from ai_lit_agent.ai_settings import AISettings, normalize_provider


@dataclass(frozen=True)
class CostEstimate:
    supported: bool
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    input_cost: float | None
    output_cost: float | None
    total_cost: float | None
    note: str


KNOWN_OPENAI_PRICES_PER_1M = {
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1": (2.00, 8.00),
    "gpt-4.1-nano": (0.10, 0.40),
    "gpt-5.6-luna": (1.00, 6.00),
    "gpt-5.6-terra": (2.50, 15.00),
    "gpt-5.6-sol": (5.00, 30.00),
}


def estimate_ai_cost(settings: AISettings, input_text: str, output_tokens: int = 1800) -> CostEstimate:
    input_tokens = estimate_tokens(input_text)
    model = settings.model.strip()
    provider = normalize_provider(settings.provider)
    if provider != "openai" or model not in KNOWN_OPENAI_PRICES_PER_1M:
        return CostEstimate(
            supported=False,
            model=model,
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=None,
            output_cost=None,
            total_cost=None,
            note="Cost estimates are currently available for known OpenAI models only.",
        )

    input_price, output_price = KNOWN_OPENAI_PRICES_PER_1M[model]
    input_cost = input_tokens / 1_000_000 * input_price
    output_cost = output_tokens / 1_000_000 * output_price
    return CostEstimate(
        supported=True,
        model=model,
        provider=provider,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_cost=input_cost,
        output_cost=output_cost,
        total_cost=input_cost + output_cost,
        note="Estimate only. Actual billing is based on provider-reported token usage.",
    )


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    # A simple, conservative approximation: English biomedical text is often near 4 chars/token.
    return max(1, (len(text) + 3) // 4)
