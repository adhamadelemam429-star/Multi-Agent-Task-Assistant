from __future__ import annotations

import re
from uuid import uuid4

from src.core.planner import Planner
from src.core.task_engine import TaskEngine
from src.llm.provider_factory import get_llm_provider
from src.tools.registry import execute_tool


class Orchestrator:
    """Coordinates planning, execution, and result review for a request."""

    def __init__(self, max_steps: int = 8, max_retries: int = 3, timeout_seconds: int = 120):
        self.planner = Planner()
        self.task_engine = TaskEngine(max_steps=max_steps, max_retries=max_retries, timeout_seconds=timeout_seconds)
        self.llm_provider = get_llm_provider()

    def handle_request(self, request_text: str, session_id: str = "default") -> dict:
        plan = self.planner.create_plan(request_text)
        task = self.task_engine.create_task(session_id=session_id, objective=request_text, task_type="general")
        task.plan = plan.model_dump()
        task.status = "running"

        execution = self.task_engine.execute_plan(plan, {"execute_tool": True})
        request_lower = request_text.lower()
        asks_datetime = any(
            phrase in request_lower
            for phrase in ("الوقت", "الساعة", "التاريخ", "what time", "current time", "today's date", "current date")
        )
        arithmetic = re.search(r"[0-9][0-9\s().+\-*/%]*[+\-*/%][0-9\s().+\-*/%]*", request_text)
        if asks_datetime:
            tool_result = execute_tool("datetime_tool")
            if tool_result["status"] == "success":
                response = f"التاريخ والوقت المحلي: {tool_result['result']['timestamp']}"
                execution["tool_results"] = [tool_result]
                execution["result"] = response
            else:
                response = f"تعذر الحصول على الوقت: {tool_result['error']}"
                execution["status"] = "failed"
                execution["result"] = response
        elif arithmetic:
            tool_result = execute_tool("calculator", {"expression": arithmetic.group().strip()})
            if tool_result["status"] == "success":
                value = tool_result["result"]
                response = f"نتيجة الحساب: {value:g}"
                if any(term in request_lower for term in ("اشرح", "فسر", "explain")):
                    expression = arithmetic.group().strip()
                    response += f"\nالشرح: حسبت التعبير {expression}، والناتج هو {value:g}."
                execution["tool_results"] = [tool_result]
                execution["result"] = response
            else:
                response = f"تعذر إجراء الحساب: {tool_result['error']}"
                execution["status"] = "failed"
                execution["result"] = response
        else:
            response = self.llm_provider.generate_response(
                request_text,
                execution_summary=execution.get("result", ""),
            )

        task.status = "completed" if execution["status"] == "completed" else "failed"
        task.result_summary = response
        task.updated_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
        return {
            "task_id": task.task_id,
            "session_id": session_id,
            "plan": plan.model_dump(),
            "execution": execution,
            "response": response,
            "status": task.status,
        }
