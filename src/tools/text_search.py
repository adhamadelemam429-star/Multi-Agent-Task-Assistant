from __future__ import annotations


def search_text(text: str, query: str, context_window: int = 80) -> list[dict[str, str | int]]:
    """Find matching snippets in text content."""
    if not text or not query:
        return []

    lower_query = query.lower()
    lower_text = text.lower()
    matches: list[dict[str, str | int]] = []
    index = 0
    while True:
        pos = lower_text.find(lower_query, index)
        if pos == -1:
            break
        start = max(0, pos - context_window)
        end = min(len(text), pos + len(query) + context_window)
        matches.append({
            "match": text[start:end].strip(),
            "start": start,
            "end": end,
        })
        index = pos + 1
    return matches
