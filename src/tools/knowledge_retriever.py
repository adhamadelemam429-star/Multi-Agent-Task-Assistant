from __future__ import annotations

from src.rag.retriever import LocalRetriever


def retrieve_relevant_chunks(query: str, chunks: list[str], top_k: int = 3) -> list[dict]:
    return LocalRetriever().retrieve(query, chunks, top_k=top_k)
