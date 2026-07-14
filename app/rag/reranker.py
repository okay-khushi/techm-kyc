from typing import Any, Dict, List

from app.utils.helpers import normalize_text


class LexicalReranker:
    """
    Lightweight, dependency-free reranker that reorders retrieved
    candidates by token-overlap with the query, blended with the
    original retrieval score. Avoids requiring a downloaded
    cross-encoder model.
    """

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        text_key: str = "text",
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:

        if not candidates:
            return []

        query_tokens = set(normalize_text(query).split())

        scored = []

        for candidate in candidates:
            text = normalize_text(str(candidate.get(text_key, "")))
            tokens = set(text.split())

            overlap = len(query_tokens & tokens) / max(len(query_tokens), 1)
            retrieval_score = candidate.get("score", 0.0)

            blended = (0.6 * overlap) + (0.4 * retrieval_score)

            scored.append({**candidate, "rerank_score": blended})

        scored.sort(key=lambda item: item["rerank_score"], reverse=True)

        return scored[:top_k]


reranker = LexicalReranker()
