import json
from typing import Any, Dict, List, Tuple

import pandas as pd

from app.services.vector_service import vector_service
from app.utils.constants import DEFAULT_TOP_K, KNOWLEDGE_DIR

GDPR_ARTICLES_CSV = KNOWLEDGE_DIR / "gdpr" / "gdpr_articles.csv"
GDPR_JSON = KNOWLEDGE_DIR / "gdpr" / "gdpr.json"


def _load_gdpr_articles() -> List[Tuple[str, Dict[str, Any]]]:
    items: List[Tuple[str, Dict[str, Any]]] = []

    if GDPR_ARTICLES_CSV.exists():
        df = pd.read_csv(GDPR_ARTICLES_CSV)

        for _, row in df.iterrows():
            text = f"{row['article_title']}. {row['article_text']}"

            items.append((
                text,
                {
                    "article_id": row["article_id"],
                    "title": row["article_title"],
                    "text": row["article_text"],
                    "source": "gdpr_articles.csv",
                },
            ))

        return items

    if GDPR_JSON.exists():
        with open(GDPR_JSON, "r", encoding="utf-8") as f:
            records = json.load(f)

        for record in records:
            text = f"{record.get('article_title', '')}. {record.get('article_text', '')}"

            items.append((
                text,
                {
                    "article_id": record.get("article_id"),
                    "title": record.get("article_title"),
                    "text": record.get("article_text"),
                    "source": "gdpr.json",
                },
            ))

    return items


class GDPRLookupTool:
    """
    Semantic search over GDPR article text, for grounding
    compliance/privacy findings in the actual regulation.
    """

    def run(self, query: str, top_k: int = DEFAULT_TOP_K) -> List[Dict]:
        return vector_service.semantic_search(
            corpus="gdpr_articles",
            query=query,
            loader=_load_gdpr_articles,
            top_k=top_k,
        )


gdpr_lookup_tool = GDPRLookupTool()
