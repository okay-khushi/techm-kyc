import re
from datetime import datetime
from typing import Any, Iterable, List, Sequence


def utcnow_iso() -> str:
    return datetime.utcnow().isoformat()


def safe_get(data: dict, *keys: str, default: Any = None) -> Any:
    """
    Safely walk a chain of nested dict keys, returning `default` if any
    key is missing along the way.
    """
    current = data

    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]

    return current


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def chunk_list(items: Sequence[Any], size: int) -> List[List[Any]]:
    if size <= 0:
        raise ValueError("size must be positive")

    return [
        list(items[i:i + size])
        for i in range(0, len(items), size)
    ]


def unique_preserve_order(items: Iterable[Any]) -> List[Any]:
    seen = set()
    result = []

    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result


def truncate(text: str, max_length: int = 500) -> str:
    if len(text) <= max_length:
        return text

    return text[:max_length].rstrip() + "..."


def contains_any(text: str, keywords: Iterable[str]) -> bool:
    normalized = normalize_text(text)

    return any(keyword.lower() in normalized for keyword in keywords)
