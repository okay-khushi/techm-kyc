from typing import Dict, List

from app.tools.gdpr_lookup import gdpr_lookup_tool
from app.tools.regulation_lookup import regulation_lookup_tool
from app.utils.constants import DEFAULT_TOP_K


class VectorSearchTool:
    """
    General-purpose semantic search across all curated knowledge
    corpora (GDPR articles + regulation reference). Used by agents that
    need broad grounding rather than a single specific lookup.
    """

    def run(self, query: str, top_k: int = DEFAULT_TOP_K) -> List[Dict]:

        results = (
            gdpr_lookup_tool.run(query, top_k=top_k)
            + regulation_lookup_tool.run(query, top_k=top_k)
        )

        results.sort(key=lambda item: item.get("rerank_score", 0), reverse=True)

        return results[:top_k]


vector_search_tool = VectorSearchTool()
