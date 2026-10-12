from __future__ import annotations

import time
from typing import Any

from src.core.exceptions import ValidationError
from src.tools.calculator import safe_calculate
from src.tools.csv_analyzer import analyze_csv
from src.tools.datetime_tool import current_datetime
from src.tools.document_reader import read_text_file
from src.tools.knowledge_retriever import retrieve_relevant_chunks
from src.tools.report_writer import write_report
from src.tools.task_manager import create_task
from src.tools.text_search import search_text

TOOL_REGISTRY: dict[str, Any] = {
    "calculator": safe_calculate,
    "text_search": search_text,
    "document_reader": read_text_file,
    "csv_analyzer": analyze_csv,
    "task_manager": create_task,
    "report_writer": write_report,
    "datetime_tool": current_datetime,
    "knowledge_retriever": retrieve_relevant_chunks,
}


def execute_tool(tool_name: str, arguments: dict[str, Any] | None = None, context: dict[str, Any] | None = None) -> dict[str, Any]:
    if tool_name not in TOOL_REGISTRY:
        raise ValidationError(f"Tool '{tool_name}' is not registered.")

    arguments = arguments or {}
    context = context or {}
    start = time.perf_counter()
    try:
        if tool_name == "calculator":
            result = TOOL_REGISTRY[tool_name](arguments["expression"])
        elif tool_name == "text_search":
            result = TOOL_REGISTRY[tool_name](arguments["text"], arguments["query"], arguments.get("context_window", 80))
        elif tool_name in {"document_reader", "csv_analyzer"}:
            result = TOOL_REGISTRY[tool_name](**arguments)
        elif tool_name == "report_writer":
            result = TOOL_REGISTRY[tool_name](arguments["content"], arguments.get("output_dir", "outputs"))
        elif tool_name == "datetime_tool":
            result = TOOL_REGISTRY[tool_name]()
        elif tool_name == "knowledge_retriever":
            result = TOOL_REGISTRY[tool_name](arguments["query"], arguments["chunks"], arguments.get("top_k", 3))
        elif tool_name == "task_manager":
            result = TOOL_REGISTRY[tool_name](arguments["task_name"], arguments.get("metadata"))
        else:
            result = TOOL_REGISTRY[tool_name](**arguments)
        duration_ms = round((time.perf_counter() - start) * 1000)
        return {"tool_name": tool_name, "status": "success", "duration_ms": duration_ms, "result": result}
    except Exception as exc:  # pragma: no cover - explicit tool safety boundary
        duration_ms = round((time.perf_counter() - start) * 1000)
        return {"tool_name": tool_name, "status": "failed", "duration_ms": duration_ms, "error": str(exc)}
