import threading
from typing import Any, Callable, Dict, List, Tuple

from app.rag.embeddings import embedding_service
from app.rag.vectorstore import VectorStore
from app.utils.constants import DEFAULT_TOP_K

SourceLoader = Callable[[], List[Tuple[str, Dict[str, Any]]]]


class Retriever:
    """
    Ties together embeddings + vector store for a named corpus. The
    store is built once (lazily, on first use) from a `SourceLoader`
    that yields (text, metadata) pairs, then persisted to disk so
    subsequent process restarts don't re-embed the corpus.
    """

    def __init__(self):
        self._stores: Dict[str, VectorStore] = {}
        self._lock = threading.Lock()

    def get_or_build_store(self, name: str, loader: SourceLoader) -> VectorStore:
        with self._lock:
            if name in self._stores:
                return self._stores[name]

            store = VectorStore.load(name, embedding_service.dimension)

            if store is None:
                items = loader()
                texts = [text for text, _ in items]
                metadatas = [meta for _, meta in items]

                store = VectorStore(name, embedding_service.dimension)

                if texts:
                    vectors = embedding_service.embed(texts)
                    store.add(vectors, metadatas)

                store.save()

            self._stores[name] = store

            return store

    def search(
        self,
        name: str,
        query: str,
        loader: SourceLoader,
        top_k: int = DEFAULT_TOP_K,
    ) -> List[Dict[str, Any]]:

        store = self.get_or_build_store(name, loader)

        if len(store) == 0:
            return []

        query_vector = embedding_service.embed([query], is_query=True)[0]
        results = store.search(query_vector, top_k=top_k)

        return [
            {**metadata, "score": score}
            for metadata, score in results
        ]


retriever = Retriever()
