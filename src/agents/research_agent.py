from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    name = "research"

    def run(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        return {
            "agent": self.name,
            "task": task,
            "summary": "Research phase collected the relevant context and mapped the task to the safest available local actions.",
            "sources": context.get("sources", []),
            "status": "completed",
        }
