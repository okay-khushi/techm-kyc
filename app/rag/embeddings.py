import hashlib
from typing import List

import numpy as np

from app.telemetry.logger import get_logger
from app.utils.constants import EMBEDDING_DIM_FALLBACK, EMBEDDING_MODEL_NAME

logger = get_logger()


class HashingEmbedder:
    """
    Deterministic, dependency-free fallback embedder using feature
    hashing over word tokens. Used when the sentence-transformers model
    cannot be loaded (e.g. no network access to download it).
    """

    def __init__(self, dim: int = EMBEDDING_DIM_FALLBACK):
        self.dim = dim

    def encode(self, texts: List[str]) -> np.ndarray:
        vectors = np.zeros((len(texts), self.dim), dtype="float32")

        for row, text in enumerate(texts):
            for token in text.lower().split():
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:4], "big") % self.dim
                sign = 1.0 if digest[4] % 2 == 0 else -1.0
                vectors[row, index] += sign

            norm = np.linalg.norm(vectors[row])

            if norm > 0:
                vectors[row] /= norm

        return vectors


class EmbeddingService:
    """
    Lazily loads a sentence-transformers model for embeddings, falling
    back to a hashing-based embedder if the model is unavailable.
    """

    def __init__(self):
        self._model = None
        self._fallback = None
        self._dim = None

    def _load_model(self):
        if self._model is not None or self._fallback is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(EMBEDDING_MODEL_NAME)

            if hasattr(self._model, "get_embedding_dimension"):
                self._dim = self._model.get_embedding_dimension()
            else:
                self._dim = self._model.get_sentence_embedding_dimension()

        except Exception as exc:
            logger.warning(
                "Falling back to hashing embedder "
                f"(could not load '{EMBEDDING_MODEL_NAME}'): {exc}"
            )

            self._fallback = HashingEmbedder()
            self._dim = self._fallback.dim

    @property
    def dimension(self) -> int:
        self._load_model()

        return self._dim

    def embed(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dimension), dtype="float32")

        self._load_model()

        if self._model is not None:
            vectors = self._model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )

            return np.asarray(vectors, dtype="float32")

        return self._fallback.encode(texts)


embedding_service = EmbeddingService()
