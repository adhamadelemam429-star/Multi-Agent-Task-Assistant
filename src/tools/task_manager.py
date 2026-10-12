from __future__ import annotations

from uuid import uuid4


def create_task(task_name: str, metadata: dict | None = None) -> dict[str, str | dict | None]:
    if not task_name or not task_name.strip():
        raise ValueError("task_name cannot be empty")
    return {
        "task_id": f"task-{uuid4().hex[:8]}",
        "status": "created",
        "task_name": task_name,
        "metadata": metadata or {},
    }
