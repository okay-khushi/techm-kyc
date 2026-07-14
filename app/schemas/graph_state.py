from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict


class GraphStateSchema(BaseModel):
    """
    Pydantic mirror of `app.orchestrator.state.GraphState`, used to
    validate/serialize the final graph output before it leaves the API.
    """

    model_config = ConfigDict(extra="allow")

    contract_text: str = ""
    sow_text: str = ""
    metadata: Dict[str, Any] = {}

    investigation_summary: str = ""
    entities: List[Dict[str, Any]] = []
    red_flags: List[Dict[str, Any]] = []

    evidence: List[Dict[str, Any]] = []

    compliance_findings: List[str] = []
    privacy_findings: List[str] = []

    risk_score: int = 0
    confidence: float = 0.0
    risk_analysis: str = ""
    validated_findings: List[Dict[str, Any]] = []

    sar: Dict[str, Any] = {}

    recommendations: List[str] = []
    citations: List[str] = []

    verified: bool = False

    execution_log: List[Dict[str, Any]] = []
