from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.core.exceptions import ValidationError


def analyze_csv(file_path: str) -> dict:
    """Analyze a local CSV file and return safe summary statistics."""
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise ValidationError(f"CSV file not found: {file_path}")
    if path.suffix.lower() != ".csv":
        raise ValidationError("Only CSV files are supported by this tool.")

    try:
        df = pd.read_csv(path)
    except Exception as exc:  # pragma: no cover - explicit error field
        raise ValidationError(f"Unable to read CSV: {exc}") from exc

    if df.empty:
        return {"row_count": 0, "column_count": 0, "columns": [], "missing_values": {}, "summary": "CSV file is empty."}

    summary = df.describe(include="all").to_dict()
    row_count = len(df)
    column_count = len(df.columns)
    missing = df.isna().sum().to_dict()
    return {
        "row_count": row_count,
        "column_count": column_count,
        "columns": list(df.columns),
        "missing_values": {str(k): int(v) for k, v in missing.items()},
        "summary": summary,
    }
