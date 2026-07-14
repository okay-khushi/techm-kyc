from typing import Dict, List

from app.rag.chunker import chunk_text
from app.utils.constants import DEFAULT_TOP_K
from app.utils.helpers import normalize_text


class ContractSearchTool:
    """
    Ad-hoc lexical search over the contract/SOW text supplied with the
    current request. The document is per-request, so it is chunked and
    scored in memory rather than persisted to a vector store.
    """

    def run(
        self,
        query: str,
        contract_text: str = "",
        sow_text: str = "",
        top_k: int = DEFAULT_TOP_K,
    ) -> List[Dict]:

        chunks = chunk_text(contract_text) + chunk_text(sow_text)

        if not chunks:
            return []

        query_tokens = set(normalize_text(query).split())

        scored = []

        for chunk in chunks:
            tokens = set(normalize_text(chunk).split())
            overlap = len(query_tokens & tokens) / max(len(query_tokens), 1)

            if overlap > 0:
                scored.append({"text": chunk, "score": overlap})

        scored.sort(key=lambda item: item["score"], reverse=True)

        return scored[:top_k]


contract_search_tool = ContractSearchTool()
