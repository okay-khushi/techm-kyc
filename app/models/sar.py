from pydantic import BaseModel
from typing import List


class SARReport(BaseModel):

    generated_at: str

    summary: str

    risk_score: int

    confidence: float

    compliance_findings: List[str]

    privacy_findings: List[str]

    recommendations: List[str]