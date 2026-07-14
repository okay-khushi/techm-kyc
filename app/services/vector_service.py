from typing import Any, Dict, List

from app.rag.reranker import reranker
from app.rag.retriever import SourceLoader, retriever
from app.utils.constants import DEFAULT_TOP_K


class VectorService:
    """
    High-level semantic search used by tools: retrieves candidates from
    a named corpus and reranks them lexically before returning.
    """

    def semantic_search(
        self,
        corpus: str,
        query: str,
        loader: SourceLoader,
        top_k: int = DEFAULT_TOP_K,
    ) -> List[Dict[str, Any]]:

        candidates = retriever.search(
            name=corpus,
            query=query,
            loader=loader,
            top_k=top_k * 3,
        )

        return reranker.rerank(query, candidates, text_key="text", top_k=top_k)


vector_service = VectorService()
