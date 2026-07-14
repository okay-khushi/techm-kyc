from typing import List

import numpy as np

from app.rag.embeddings import embedding_service as _embedding_service


class EmbeddingService:
    """
    Thin service-layer wrapper around the RAG embedding backend, kept
    separate so agents/services never import from `app.rag` directly.
    """

    def embed(self, text: str) -> np.ndarray:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        return _embedding_service.embed(texts)


embedding_service = EmbeddingService()
