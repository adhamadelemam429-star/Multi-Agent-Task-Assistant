from __future__ import annotations

from src.llm.base_provider import BaseLLMProvider
from src.llm.demo_provider import DemoLLMProvider


def get_llm_provider(provider_name: str | None = None) -> BaseLLMProvider:
    name = (provider_name or "demo").lower()
    if name in {"demo", "mock"}:
        return DemoLLMProvider()
    raise ValueError(f"Unsupported LLM provider: {provider_name}")
