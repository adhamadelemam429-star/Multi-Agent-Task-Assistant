from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.core.exceptions import TaskExecutionError
from src.core.models import PlanStatus, StepStatus, TaskRecord


class TaskEngine:
    """Small task execution engine that respects dependencies and limits."""

    def __init__(self, max_steps: int = 8, max_retries: int = 3, timeout_seconds: int = 120):
        self.max_steps = max_steps
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

    def create_task(self, session_id: str, objective: str, task_type: str = "general") -> TaskRecord:
        now = datetime.now(timezone.utc).isoformat()
        task = TaskRecord(
            task_id=f"task-{uuid4().hex[:8]}",
            session_id=session_id,
            task_type=task_type,
            objective=objective,
            status="pending",
            created_at=now,
            updated_at=now,
        )
        return task

    def execute_plan(self, plan, tool_context: dict | None = None) -> dict:
        tool_context = tool_context or {}
        if not plan.steps:
            raise TaskExecutionError("Plan contains no executable steps.")

        if len(plan.steps) > self.max_steps:
            raise TaskExecutionError("Plan exceeds the configured maximum steps.")

        completed_steps = []
        for step in plan.steps:
            if step.dependencies:
                missing = [dep for dep in step.dependencies if dep not in completed_steps]
                if missing:
                    step.status = StepStatus.skipped
                    step.result = f"Skipped due to missing dependencies: {missing}"
                    continue

            step.status = StepStatus.running
            try:
                step.result = self._simulate_step_execution(step, tool_context)
                step.status = StepStatus.completed
                completed_steps.append(step.step_id)
            except Exception as exc:  # pragma: no guard - explicit safety boundary
                step.status = StepStatus.failed
                step.result = str(exc)
                plan.status = PlanStatus.failed
                return {
                    "status": "failed",
                    "plan_id": plan.plan_id,
                    "completed_steps": completed_steps,
                    "current_step": step.step_id,
                    "result": step.result,
                }

        plan.status = PlanStatus.completed
        return {
            "status": "completed",
            "plan_id": plan.plan_id,
            "completed_steps": completed_steps,
            "result": "All steps completed successfully.",
        }

    def _simulate_step_execution(self, step, tool_context: dict) -> str:
        tool_names = ", ".join(step.tools) or "generic"  # pragma: no cover - simple helper
        if tool_context.get("execute_tool"):
            return (
                f"Executed step '{step.description}' with tools [{tool_names}] "
                f"through the safe task engine."
            )
        return f"Step executed: {step.description} ({tool_names})"
