from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from src.api.schemas import ChatMessageRequest, KnowledgeDocumentRequest, SessionCreateRequest, TaskCreateRequest
from src.core.orchestrator import Orchestrator
from src.memory.database import init_db
from src.memory.session_manager import SessionManager
from src.rag.chunker import Chunker

init_db()

app = FastAPI(title="Multi-Agent AI Task Assistant", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_manager = SessionManager()
orchestrator = Orchestrator(max_steps=settings.MAX_AGENT_STEPS, max_retries=settings.MAX_RETRIES, timeout_seconds=settings.TASK_TIMEOUT_SECONDS)


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok", "mode": "demo", "provider": settings.LLM_PROVIDER}


@app.get("/api/v1/config")
def get_config() -> dict:
    return {
        "app_env": settings.APP_ENV,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "database_url": settings.DATABASE_URL,
        "max_agent_steps": settings.MAX_AGENT_STEPS,
        "max_retries": settings.MAX_RETRIES,
        "task_timeout_seconds": settings.TASK_TIMEOUT_SECONDS,
        "max_tool_calls": settings.MAX_TOOL_CALLS,
    }


@app.post("/api/v1/sessions")
def create_session(payload: SessionCreateRequest) -> dict:
    session = session_manager.create_session(language=payload.language, mode=payload.mode)
    return session


@app.get("/api/v1/sessions/{session_id}")
def get_session(session_id: str) -> dict:
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session": session, "history": session_manager.get_conversation_history(session_id)}


@app.delete("/api/v1/sessions/{session_id}")
def delete_session(session_id: str) -> dict:
    if not session_manager.get_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    session_manager.delete_session(session_id)
    return {"status": "deleted", "session_id": session_id}


@app.post("/api/v1/chat")
def chat(payload: ChatMessageRequest) -> dict:
    if not session_manager.get_session(payload.session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    session_manager.save_message(payload.session_id, "user", payload.message)
    result = orchestrator.handle_request(payload.message, session_id=payload.session_id)
    session_manager.save_message(payload.session_id, "assistant", result["response"])
    session_manager.save_task({
        "task_id": result["task_id"],
        "session_id": payload.session_id,
        "task_type": "chat",
        "objective": payload.message,
        "status": result["status"],
        "plan": result["plan"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "result_summary": result["response"],
    })
    return {
        "session_id": payload.session_id,
        "response": result["response"],
        "task_id": result["task_id"],
        "status": result["status"],
    }


@app.post("/api/v1/tasks")
def create_task(payload: TaskCreateRequest) -> dict:
    if not session_manager.get_session(payload.session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    result = orchestrator.handle_request(payload.objective, session_id=payload.session_id)
    session_manager.save_task({
        "task_id": result["task_id"],
        "session_id": payload.session_id,
        "task_type": payload.task_type,
        "objective": payload.objective,
        "status": result["status"],
        "plan": result["plan"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "result_summary": result["response"],
    })
    return {
        "task_id": result["task_id"],
        "status": result["status"],
        "plan": result["plan"],
        "execution": result["execution"],
    }


@app.get("/api/v1/tasks/{task_id}")
def get_task(task_id: str) -> dict:
    task = session_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/api/v1/tasks/{task_id}/cancel")
def cancel_task(task_id: str) -> dict:
    task = session_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task["status"] = "cancelled"
    task["updated_at"] = datetime.now(timezone.utc).isoformat()
    session_manager.save_task(task)
    return {"task_id": task_id, "status": "cancelled"}


@app.post("/api/v1/knowledge/documents")
def create_knowledge_document(payload: KnowledgeDocumentRequest) -> dict:
    knowledge_doc_id = f"doc-{uuid4().hex[:8]}"
    chunks = Chunker(chunk_size=250, overlap=50).chunk_text(payload.content)
    with __import__("src.memory.database", fromlist=["get_connection"]).get_connection() as conn:
        conn.execute(
            "INSERT INTO knowledge_documents(document_id, title, source_path, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (knowledge_doc_id, payload.title, payload.source_path, payload.content, datetime.now(timezone.utc).isoformat()),
        )
        for index, chunk in enumerate(chunks):
            conn.execute(
                "INSERT INTO knowledge_chunks(chunk_id, document_id, content, chunk_index, metadata) VALUES (?, ?, ?, ?, ?)",
                (f"chunk-{uuid4().hex[:8]}", knowledge_doc_id, chunk, index, "{}"),
            )
    return {"document_id": knowledge_doc_id, "chunk_count": len(chunks), "title": payload.title}


@app.get("/api/v1/knowledge/documents")
def get_knowledge_documents() -> list[dict]:
    with __import__("src.memory.database", fromlist=["get_connection"]).get_connection() as conn:
        rows = conn.execute("SELECT * FROM knowledge_documents ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]


@app.delete("/api/v1/knowledge/documents/{document_id}")
def delete_knowledge_document(document_id: str) -> dict:
    with __import__("src.memory.database", fromlist=["get_connection"]).get_connection() as conn:
        conn.execute("DELETE FROM knowledge_chunks WHERE document_id = ?", (document_id,))
        conn.execute("DELETE FROM knowledge_documents WHERE document_id = ?", (document_id,))
    return {"status": "deleted", "document_id": document_id}
