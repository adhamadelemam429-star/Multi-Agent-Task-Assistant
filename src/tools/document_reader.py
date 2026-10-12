from __future__ import annotations

from pathlib import Path

from src.core.exceptions import ValidationError

_ALLOWED_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".log"}


def read_text_file(file_path: str, allowed_base_dir: str | None = None, max_bytes: int = 2 * 1024 * 1024) -> dict[str, str | int]:
    """Safely read a text-based file from an allowed directory."""
    target = Path(file_path)
    if not target.exists() or not target.is_file():
        raise ValidationError(f"File not found: {file_path}")

    if target.suffix.lower() not in _ALLOWED_EXTENSIONS:
        raise ValidationError(f"Unsupported file type: {target.suffix}")

    resolved = target.resolve()
    if allowed_base_dir:
        base = Path(allowed_base_dir).resolve()
        if base not in resolved.parents and resolved != base:
            raise ValidationError("Path traversal is not allowed.")

    content = resolved.read_text(encoding="utf-8", errors="replace")
    if len(content.encode("utf-8")) > max_bytes:
        raise ValidationError("File exceeds the configured maximum size.")

    return {"path": str(resolved), "content": content, "size_bytes": len(content.encode("utf-8"))}
