from typing import Any, Dict, List

from pydantic import BaseModel


class AnalysisResult(BaseModel):
    """
    Internal, normalized representation of a completed graph execution,
    independent of the wire format used by the API layer.
    """

    summary: str
    risk_score: int
    confidence: float
    compliance_findings: List[str] = []
    privacy_findings: List[str] = []
    evidence: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    citations: List[str] = []
    verified: bool = False
    sar: Dict[str, Any] = {}

    @classmethod
    def from_state(cls, state: Dict[str, Any]) -> "AnalysisResult":
        return cls(
            summary=state.get("investigation_summary", ""),
            risk_score=state.get("risk_score", 0),
            confidence=state.get("confidence", 0.0),
            compliance_findings=state.get("compliance_findings", []),
            privacy_findings=state.get("privacy_findings", []),
            evidence=state.get("evidence", []),
            recommendations=state.get("recommendations", []),
            citations=state.get("citations", []),
            verified=state.get("verified", False),
            sar=state.get("sar", {}),
        )
