from __future__ import annotations


class Chunker:
    """Creates fixed-size text chunks with overlap."""

    def __init__(self, chunk_size: int = 250, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> list[str]:
        if not text:
            return []
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(len(text), start + self.chunk_size)
            chunk = text[start:end]
            chunks.append(chunk)
            if end >= len(text):
                break
            start += self.chunk_size - self.overlap
        return chunks
