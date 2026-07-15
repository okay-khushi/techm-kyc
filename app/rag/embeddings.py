import hashlib
from typing import List

import httpx
import numpy as np

from app.config.settings import settings
from app.telemetry.logger import get_logger
from app.utils.constants import EMBEDDING_DIM_FALLBACK, EMBEDDING_MODEL_NAME

logger = get_logger()

NVIDIA_EMBEDDINGS_URL = "https://integrate.api.nvidia.com/v1/embeddings"
NVIDIA_MAX_BATCH_SIZE = 512  # NIM's e5-v5 batcher rejects requests over 1024 inputs


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


class NimEmbedder:
    """
    Calls NVIDIA NIM's hosted embeddings API instead of running a model
    locally. Chosen once at startup (see `EmbeddingService._load_model`)
    when `NVIDIA_API_KEY` is configured; never mixed at runtime with the
    local model/hashing fallback, since switching embedders mid-corpus
    would put vectors from different spaces in the same index.
    """

    def __init__(self, api_key: str, model: str):
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            timeout=30.0,
        )
        self._model = model

    def encode(self, texts: List[str], input_type: str = "passage") -> np.ndarray:
        batches = [
            texts[i:i + NVIDIA_MAX_BATCH_SIZE]
            for i in range(0, len(texts), NVIDIA_MAX_BATCH_SIZE)
        ] or [[]]

        vectors = np.vstack([self._encode_batch(batch, input_type) for batch in batches])

        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0

        return vectors / norms

    def _encode_batch(self, texts: List[str], input_type: str) -> np.ndarray:
        response = self._client.post(
            NVIDIA_EMBEDDINGS_URL,
            json={
                "input": texts,
                "model": self._model,
                "input_type": input_type,
                "encoding_format": "float",
                "truncate": "NONE",
            },
        )
        response.raise_for_status()

        data = sorted(response.json()["data"], key=lambda item: item["index"])

        return np.array([item["embedding"] for item in data], dtype="float32")


class EmbeddingService:
    """
    Lazily picks an embedder, in order of preference: NVIDIA NIM (if
    `NVIDIA_API_KEY` is set and reachable), then a local
    sentence-transformers model, then a dependency-free hashing
    embedder. The choice is made once and kept for the process
    lifetime — see `NimEmbedder` docstring for why.
    """

    def __init__(self):
        self._model = None
        self._nim = None
        self._fallback = None
        self._dim = None

    def _load_model(self):
        if self._model is not None or self._nim is not None or self._fallback is not None:
            return

        if settings.NVIDIA_API_KEY:
            try:
                nim = NimEmbedder(settings.NVIDIA_API_KEY, settings.NVIDIA_EMBEDDING_MODEL)
                probe = nim.encode(["healthcheck"], input_type="query")

                self._nim = nim
                self._dim = probe.shape[1]

                return

            except Exception as exc:
                logger.warning(
                    "Falling back from NVIDIA NIM embeddings "
                    f"('{settings.NVIDIA_EMBEDDING_MODEL}'): {exc}"
                )

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

    def embed(self, texts: List[str], is_query: bool = False) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dimension), dtype="float32")

        self._load_model()

        if self._nim is not None:
            return self._nim.encode(texts, input_type="query" if is_query else "passage")

        if self._model is not None:
            vectors = self._model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )

            return np.asarray(vectors, dtype="float32")

        return self._fallback.encode(texts)


embedding_service = EmbeddingService()
