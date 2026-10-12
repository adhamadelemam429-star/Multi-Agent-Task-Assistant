from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent


class DataAnalystAgent(BaseAgent):
    name = "data_analyst"

    def run(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        file_path = context.get("file_path")
        analysis = context.get("analysis", {})
        summary = {
            "agent": self.name,
            "task": task,
            "status": "completed",
            "file_path": file_path,
            "analysis": analysis,
        }
        if analysis:
            summary["notes"] = "Summary statistics were computed from the provided dataset using safe local analysis." 
        return summary
