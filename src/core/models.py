from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class PlanStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class StepStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"
    cancelled = "cancelled"


class AgentRole(str, Enum):
    orchestrator = "orchestrator"
    planner = "planner"
    research = "research"
    data_analyst = "data_analyst"
    coding = "coding"
    reviewer = "reviewer"


class PlanStep(BaseModel):
    step_id: str
    description: str
    agent: str
    dependencies: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    success_criteria: str
    status: StepStatus = StepStatus.pending
    result: str | None = None


class TaskPlan(BaseModel):
    plan_id: str
    objective: str
    steps: list[PlanStep] = Field(default_factory=list)
    status: PlanStatus = PlanStatus.pending
    summary: str | None = None


class ToolCallRecord(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    status: str = "success"
    duration_ms: int = 0
    result: str | None = None
    error: str | None = None


class TaskRecord(BaseModel):
    task_id: str
    session_id: str
    task_type: str = "general"
    objective: str
    status: Literal["pending", "running", "completed", "failed", "skipped", "cancelled"] = "pending"
    plan: dict[str, Any] | None = None
    created_at: str | None = None
    updated_at: str | None = None
    result_summary: str | None = None


class ChatMessage(BaseModel):
    message_id: str
    session_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: str | None = None


class SessionRecord(BaseModel):
    session_id: str
    created_at: str | None = None
    last_activity_at: str | None = None
    language: str = "en"
    mode: str = "demo"
