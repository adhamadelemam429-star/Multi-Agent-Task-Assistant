from __future__ import annotations

from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    language: str = "en"
    mode: str = "demo"


class ChatMessageRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    language: str = "en"


class TaskCreateRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    objective: str = Field(..., min_length=1)
    task_type: str = "general"


class KnowledgeDocumentRequest(BaseModel):
    title: str = Field(..., min_length=1)
    source_path: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
