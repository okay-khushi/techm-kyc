from typing import Any, Dict, List, Tuple

import pandas as pd

from app.services.vector_service import vector_service
from app.utils.constants import CSV_CHUNK_SIZE, DEFAULT_TOP_K, KNOWLEDGE_DIR, MAX_SCAN_CHUNKS

OPP_ANNOTATIONS_DIR = KNOWLEDGE_DIR / "privacy" / "meta-annotations" / "OPP-115 Annotations"
OPP_CATEGORIES = [
    "first", "third", "datasecurity", "dataretention",
    "user_access", "user_choice", "other",
]


def _load_opp_annotations() -> List[Tuple[str, Dict[str, Any]]]:
    items: List[Tuple[str, Dict[str, Any]]] = []

    for filename in ("train_opp_annotations.csv", "test_opp_annotations.csv"):
        path = OPP_ANNOTATIONS_DIR / filename

        if not path.exists():
            continue

        df = pd.read_csv(path, sep="\t")

        for _, row in df.iterrows():
            categories = [c for c in OPP_CATEGORIES if row.get(c, 0) == 1]

            items.append((
                str(row["Query"]),
                {
                    "query_id": row["QueryID"],
                    "doc_id": row["DocID"],
                    "categories": categories,
                    "text": row["Query"],
                    "source": filename,
                },
            ))

    return items


def _find_relevant_segments(query_id: str, limit: int = 3) -> List[str]:
    """
    Best-effort scan of policy_train_data.csv for "Relevant" segments
    tied to a given OPP-115 QueryID. Bounded by MAX_SCAN_CHUNKS since
    the source file has 180k+ rows.
    """

    path = KNOWLEDGE_DIR / "privacy" / "policy_train_data.csv"

    if not path.exists():
        return []

    segments: List[str] = []

    for i, chunk in enumerate(pd.read_csv(path, sep="\t", chunksize=CSV_CHUNK_SIZE)):
        matches = chunk[
            (chunk["QueryID"] == query_id) & (chunk["Label"] == "Relevant")
        ]

        segments.extend(matches["Segment"].astype(str).tolist())

        if len(segments) >= limit or i + 1 >= MAX_SCAN_CHUNKS:
            break

    return segments[:limit]


class PolicyLookupTool:
    """
    Semantic search over OPP-115 privacy-policy query annotations,
    returning which policy category (data retention, user choice,
    third-party sharing, ...) best matches a query.
    """

    def run(self, query: str, top_k: int = DEFAULT_TOP_K, with_segments: bool = False) -> List[Dict]:

        results = vector_service.semantic_search(
            corpus="opp115_annotations",
            query=query,
            loader=_load_opp_annotations,
            top_k=top_k,
        )

        if with_segments:
            for result in results:
                result["example_segments"] = _find_relevant_segments(result.get("query_id"))

        return results


policy_lookup_tool = PolicyLookupTool()
