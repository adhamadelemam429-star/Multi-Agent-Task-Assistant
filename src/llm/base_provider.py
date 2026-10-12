from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """Abstract model provider interface."""

    name: str = "base"

    @abstractmethod
    def generate_response(self, prompt: str, **kwargs: Any) -> str:
        """Return a plain-text response for a prompt."""

    @abstractmethod
    def generate_structured_output(self, prompt: str, schema: Any | None = None, **kwargs: Any) -> dict[str, Any]:
        """Return a structured object for prompt-driven generation."""

    def is_available(self) -> bool:
        return True
