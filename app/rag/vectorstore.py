import json
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from app.utils.constants import CACHE_DIR

VECTORSTORE_DIR = CACHE_DIR / "vectorstore"


class VectorStore:
    """
    Simple persisted vector store. Uses FAISS for similarity search when
    available, otherwise falls back to brute-force cosine similarity
    with numpy so the app still works without a compiled faiss wheel.
    """

    def __init__(self, name: str, dim: int):
        self.name = name
        self.dim = dim
        self._lock = threading.Lock()

        self.vectors: np.ndarray = np.zeros((0, dim), dtype="float32")
        self.metadatas: List[Dict[str, Any]] = []

        self._faiss_index = None
        self._use_faiss = self._try_import_faiss()

    def _try_import_faiss(self) -> bool:
        try:
            import faiss  # noqa: F401

            return True

        except Exception:
            return False

    def add(self, vectors: np.ndarray, metadatas: List[Dict[str, Any]]):
        with self._lock:
            if vectors.shape[0] == 0:
                return

            self.vectors = (
                vectors.copy()
                if self.vectors.shape[0] == 0
                else np.vstack([self.vectors, vectors])
            )
            self.metadatas.extend(metadatas)
            self._faiss_index = None

    def _build_faiss(self):
        import faiss

        index = faiss.IndexFlatIP(self.dim)

        if self.vectors.shape[0] > 0:
            index.add(np.ascontiguousarray(self.vectors))

        self._faiss_index = index

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
    ) -> List[Tuple[Dict[str, Any], float]]:

        if self.vectors.shape[0] == 0:
            return []

        query_vector = np.asarray(query_vector, dtype="float32").reshape(1, -1)

        if self._use_faiss:
            if self._faiss_index is None:
                self._build_faiss()

            scores, indices = self._faiss_index.search(query_vector, min(top_k, len(self.metadatas)))

            results = []

            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:
                    continue

                results.append((self.metadatas[idx], float(score)))

            return results

        scores = self.vectors @ query_vector[0]
        top_indices = np.argsort(-scores)[:top_k]

        return [
            (self.metadatas[i], float(scores[i]))
            for i in top_indices
        ]

    def save(self):
        VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

        np.save(VECTORSTORE_DIR / f"{self.name}.npy", self.vectors)

        with open(VECTORSTORE_DIR / f"{self.name}.meta.json", "w", encoding="utf-8") as f:
            json.dump(self.metadatas, f)

    @classmethod
    def load(cls, name: str, dim: int) -> Optional["VectorStore"]:
        vectors_path = VECTORSTORE_DIR / f"{name}.npy"
        meta_path = VECTORSTORE_DIR / f"{name}.meta.json"

        if not vectors_path.exists() or not meta_path.exists():
            return None

        vectors = np.load(vectors_path)

        if vectors.shape[1] != dim:
            # Embedding provider/model changed since this store was
            # persisted (e.g. switching to/from NVIDIA NIM) — its
            # vectors live in a different space, so rebuild from source
            # instead of returning a store that can't be searched.
            return None

        store = cls(name, dim)
        store.vectors = vectors

        with open(meta_path, "r", encoding="utf-8") as f:
            store.metadatas = json.load(f)

        return store

    def __len__(self) -> int:
        return len(self.metadatas)
