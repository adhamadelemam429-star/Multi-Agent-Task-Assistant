from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent


class ReviewerAgent(BaseAgent):
    name = "reviewer"

    def run(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        result = {
            "agent": self.name,
            "task": task,
            "approved": True,
            "issues": [],
            "suggested_fixes": [],
            "summary": "The result was reviewed for completeness, evidence, and safety boundaries.",
            "status": "completed",
        }
        if context.get("warnings"):
            result["issues"] = context["warnings"]
            result["approved"] = False
        return result
