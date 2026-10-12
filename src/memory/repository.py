from __future__ import annotations

import json
from datetime import datetime, timezone

from src.memory.database import get_connection


class MemoryRepository:
    def __init__(self):
        self._conn = get_connection()

    def create_session(self, session_id: str, language: str = "en", mode: str = "demo") -> dict:
        now = datetime.now(timezone.utc).isoformat()
        with get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO sessions(session_id, created_at, last_activity_at, language, mode) VALUES (?, ?, ?, ?, ?)",
                (session_id, now, now, language, mode),
            )
        return {"session_id": session_id, "language": language, "mode": mode, "created_at": now}

    def get_session(self, session_id: str) -> dict | None:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
            return dict(row) if row else None

    def save_message(self, message_id: str, session_id: str, role: str, content: str) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        with get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO messages(message_id, session_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                (message_id, session_id, role, content, now),
            )
        return {"message_id": message_id, "session_id": session_id, "role": role, "content": content, "created_at": now}

    def get_conversation_history(self, session_id: str) -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC",
                (session_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def save_task(self, task_record: dict) -> dict:
        with get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tasks(task_id, session_id, task_type, objective, status, plan, created_at, updated_at, result_summary) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    task_record["task_id"],
                    task_record["session_id"],
                    task_record["task_type"],
                    task_record["objective"],
                    task_record["status"],
                    json.dumps(task_record.get("plan")) if task_record.get("plan") else None,
                    task_record.get("created_at"),
                    task_record.get("updated_at"),
                    task_record.get("result_summary"),
                ),
            )
        return task_record

    def get_task(self, task_id: str) -> dict | None:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
            if not row:
                return None
            data = dict(row)
            if data.get("plan"):
                data["plan"] = json.loads(data["plan"])
            return data

    def clear_session(self, session_id: str) -> None:
        with get_connection() as conn:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM tasks WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

    def delete_session(self, session_id: str) -> None:
        self.clear_session(session_id)
