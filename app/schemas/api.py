from pydantic import BaseModel
from typing import Optional


class AnalyzeRequest(BaseModel):

    contract_text: str

    sow_text: Optional[str] = ""

    metadata: dict = {}


class AnalyzeResponse(BaseModel):

    summary: str

    findings: list

    evidence: list

    confidence: float

    verified: bool