from __future__ import annotations

from pathlib import Path

from src.tools.document_reader import read_text_file


class DocumentLoader:
    """Loads text documents from the configured workspace and stores their metadata."""

    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir).resolve()

    def load_document(self, file_path: str) -> dict:
        return read_text_file(file_path=file_path, allowed_base_dir=str(self.base_dir), max_bytes=2 * 1024 * 1024)
