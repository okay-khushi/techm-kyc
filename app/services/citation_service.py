from typing import Any, Dict, List


class CitationService:
    """
    Builds a flat, human-readable citation trail from everything an
    investigation gathered: evidence, compliance/privacy findings, and
    any retrieved knowledge-base sources.
    """

    def build_citations(
        self,
        evidence: List[Dict[str, Any]],
        compliance_findings: List[str],
        privacy_findings: List[str],
        retrieved_sources: List[Dict[str, Any]] = None,
    ) -> List[str]:

        citations = []

        for i, item in enumerate(evidence, start=1):
            description = item.get("description", "") if isinstance(item, dict) else str(item)
            source = item.get("source") if isinstance(item, dict) else None
            tag = f"source={source}" if source else f"type={item.get('type', 'unknown')}" if isinstance(item, dict) else "type=unknown"

            citations.append(f"[Evidence {i}] ({tag}) {description}")

        for i, finding in enumerate(compliance_findings, start=1):
            citations.append(f"[Compliance {i}] {finding}")

        for i, finding in enumerate(privacy_findings, start=1):
            citations.append(f"[Privacy {i}] {finding}")

        for item in retrieved_sources or []:
            label = item.get("id") or item.get("article_id") or item.get("name") or "source"
            citations.append(f"[Reference: {label}] {item.get('text', '')}".strip())

        return citations


citation_service = CitationService()
