from __future__ import annotations

from uuid import uuid4

from src.memory.repository import MemoryRepository


class SessionManager:
    def __init__(self):
        self.repository = MemoryRepository()

    def create_session(self, language: str = "en", mode: str = "demo") -> dict:
        session_id = f"session-{uuid4().hex[:8]}"
        return self.repository.create_session(session_id, language=language, mode=mode)

    def get_session(self, session_id: str) -> dict | None:
        return self.repository.get_session(session_id)

    def save_message(self, session_id: str, role: str, content: str) -> dict:
        message_id = f"msg-{uuid4().hex[:8]}"
        return self.repository.save_message(message_id, session_id, role, content)

    def get_conversation_history(self, session_id: str) -> list[dict]:
        return self.repository.get_conversation_history(session_id)

    def save_task(self, task_record: dict) -> dict:
        return self.repository.save_task(task_record)

    def get_task(self, task_id: str) -> dict | None:
        return self.repository.get_task(task_id)

    def clear_session(self, session_id: str) -> None:
        self.repository.clear_session(session_id)

    def delete_session(self, session_id: str) -> None:
        self.repository.delete_session(session_id)
