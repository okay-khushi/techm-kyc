from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ReportSchema(BaseModel):

    generated_at: str
    summary: str
    risk_score: int
    confidence: float
    compliance_findings: List[str] = []
    privacy_findings: List[str] = []
    evidence: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    citations: List[str] = []
    llm_summary: Optional[str] = None
    verification: Optional[Dict[str, Any]] = None
