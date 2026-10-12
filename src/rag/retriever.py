from __future__ import annotations

import math
import re
from collections import Counter


class LocalRetriever:
    """Lightweight local retriever using bag-of-words similarity."""

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"\b\w+\b", text.lower())

    def retrieve(self, query: str, chunks: list[str], top_k: int = 3) -> list[dict]:
        if not query or not chunks:
            return []

        query_tokens = Counter(self._tokenize(query))
        results: list[dict] = []
        for index, chunk in enumerate(chunks):
            chunk_tokens = Counter(self._tokenize(chunk))
            if not chunk_tokens:
                continue
            query_norm = math.sqrt(sum(v * v for v in query_tokens.values()))
            chunk_norm = math.sqrt(sum(v * v for v in chunk_tokens.values()))
            score = 0.0
            for token, q_count in query_tokens.items():
                score += q_count * chunk_tokens.get(token, 0)
            if query_norm == 0 or chunk_norm == 0:
                continue
            score = score / (query_norm * chunk_norm)
            if score > 0:
                results.append({"chunk_index": index, "score": round(score, 4), "content": chunk})
        return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]
