# API Reference

This project exposes a minimal REST API for local testing and integration.

## Health

- GET /health

Returns the runtime status and provider metadata.

## Sessions

- POST /api/v1/sessions
- GET /api/v1/sessions/{session_id}
- DELETE /api/v1/sessions/{session_id}

Creates and manages local conversation sessions.

## Chat

- POST /api/v1/chat

Request body:

```json
{
  "session_id": "session-123",
  "message": "Analyze my CSV and summarize missing values.",
  "language": "en"
}
```

Returns the assistant response and task metadata.

## Tasks

- POST /api/v1/tasks
- GET /api/v1/tasks/{task_id}
- POST /api/v1/tasks/{task_id}/cancel

Creates and fetches task state.

## Knowledge

- POST /api/v1/knowledge/documents
- GET /api/v1/knowledge/documents
- DELETE /api/v1/knowledge/documents/{document_id}

Stores and retrieves local knowledge documents.
