from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """Common interface for all specialized agents in the system."""

    name: str = "base_agent"

    @abstractmethod
    def run(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        raise NotImplementedError
