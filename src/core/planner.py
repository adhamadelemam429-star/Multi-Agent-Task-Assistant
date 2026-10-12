from __future__ import annotations

from uuid import uuid4

from src.core.exceptions import PlanningError
from src.core.models import PlanStatus, PlanStep, TaskPlan


class Planner:
    """Creates a simple but structured execution plan from a user request."""

    def create_plan(self, objective: str) -> TaskPlan:
        if not objective or not objective.strip():
            raise PlanningError("Objective cannot be empty.")

        lower = objective.lower()
        steps: list[PlanStep] = []

        if any(token in lower for token in ["csv", "excel", "data", "analy"]):
            steps = [
                PlanStep(
                    step_id="step-1",
                    description="Validate the input file and required data context.",
                    agent="research",
                    dependencies=[],
                    tools=["document_reader", "csv_analyzer"],
                    success_criteria="File exists, readable, and the task goal is clear.",
                ),
                PlanStep(
                    step_id="step-2",
                    description="Analyze structured data and compute summary statistics.",
                    agent="data_analyst",
                    dependencies=["step-1"],
                    tools=["csv_analyzer"],
                    success_criteria="Row count, missing values, and summary metrics are computed.",
                ),
                PlanStep(
                    step_id="step-3",
                    description="Draft a short result report with caveats and limitations.",
                    agent="reviewer",
                    dependencies=["step-2"],
                    tools=["report_writer"],
                    success_criteria="Final output describes findings and limits clearly.",
                ),
            ]
        elif any(token in lower for token in ["code", "python", "implement", "fix", "build"]):
            steps = [
                PlanStep(
                    step_id="step-1",
                    description="Inspect the request and workspace context.",
                    agent="research",
                    dependencies=[],
                    tools=["document_reader"],
                    success_criteria="The implementation scope is identified.",
                ),
                PlanStep(
                    step_id="step-2",
                    description="Prepare a concrete coding plan and patch content.",
                    agent="coding",
                    dependencies=["step-1"],
                    tools=["task_manager"],
                    success_criteria="A safe code draft or task plan is prepared.",
                ),
                PlanStep(
                    step_id="step-3",
                    description="Review the output for correctness and completeness.",
                    agent="reviewer",
                    dependencies=["step-2"],
                    tools=["report_writer"],
                    success_criteria="The final result is reviewed for gaps and accuracy.",
                ),
            ]
        else:
            steps = [
                PlanStep(
                    step_id="step-1",
                    description="Identify the task type and relevant source material.",
                    agent="research",
                    dependencies=[],
                    tools=["document_reader", "text_search"],
                    success_criteria="The user goal and source context are clear.",
                ),
                PlanStep(
                    step_id="step-2",
                    description="Execute the required task using safe local tools.",
                    agent="coding",
                    dependencies=["step-1"],
                    tools=["calculator", "task_manager"],
                    success_criteria="The required work is performed safely.",
                ),
                PlanStep(
                    step_id="step-3",
                    description="Produce the final response and summarize any caveats.",
                    agent="reviewer",
                    dependencies=["step-2"],
                    tools=["report_writer"],
                    success_criteria="The result is concise, evidence-based, and clear about limitations.",
                ),
            ]

        return TaskPlan(
            plan_id=f"plan-{uuid4().hex[:8]}",
            objective=objective.strip(),
            steps=steps,
            status=PlanStatus.pending,
            summary="Plan created by the planner agent.",
        )
