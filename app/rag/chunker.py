from typing import List


def chunk_text(
    text: str,
    chunk_size: int = 200,
    overlap: int = 40,
) -> List[str]:
    """
    Splits `text` into overlapping word-based chunks. Overlap keeps
    context from being cut off at chunk boundaries.
    """

    words = text.split()

    if not words:
        return []

    if overlap >= chunk_size:
        overlap = max(chunk_size // 4, 0)

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):
        chunk = words[start:start + chunk_size]

        if not chunk:
            continue

        chunks.append(" ".join(chunk))

        if start + chunk_size >= len(words):
            break

    return chunks
