from __future__ import annotations

from datetime import datetime


def current_datetime() -> dict[str, str]:
    """Return the local system date and time in ISO format."""
    return {"timestamp": datetime.now().isoformat(timespec="seconds")}
