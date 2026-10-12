from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.core.exceptions import ValidationError


def write_report(content: str, output_dir: str = "outputs") -> dict[str, str | int]:
    """Write markdown content into the project outputs directory."""
    if not content or not content.strip():
        raise ValidationError("Report content cannot be empty.")

    base_dir = Path(output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    file_name = f"report_{timestamp}.md"
    file_path = base_dir / file_name
    file_path.write_text(content, encoding="utf-8")
    return {"path": str(file_path), "filename": file_name, "size_bytes": file_path.stat().st_size}
