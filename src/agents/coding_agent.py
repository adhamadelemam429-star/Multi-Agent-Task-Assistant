from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent


class CodingAgent(BaseAgent):
    name = "coding"

    def run(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        return {
            "agent": self.name,
            "task": task,
            "summary": "Coding task prepared with a minimal safe implementation strategy and explicit verification checkpoints.",
            "workspace": context.get("workspace", "."),
            "status": "completed",
        }
