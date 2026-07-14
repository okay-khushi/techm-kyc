from typing import TypedDict, List, Dict, Any


class GraphState(TypedDict):
    """
    Shared state passed between all LangGraph nodes.
    """

    # ==========================
    # Input
    # ==========================
    contract_text: str
    sow_text: str
    metadata: Dict[str, Any]

    # ==========================
    # Investigation
    # ==========================
    investigation_summary: str
    entities: List[Dict[str, Any]]
    red_flags: List[Dict[str, Any]]

    # ==========================
    # Evidence
    # ==========================
    evidence: List[Dict[str, Any]]

    # ==========================
    # Compliance
    # ==========================
    compliance_findings: List[str]

    # ==========================
    # Privacy
    # ==========================
    privacy_findings: List[str]

    # ==========================
    # Risk
    # ==========================
    risk_score: int
    confidence: float
    risk_analysis: str
    validated_findings: List[Dict[str, Any]]

    # ==========================
    # Reasoning / Contradiction / Remediation / Explainability
    # ==========================
    reasoning_summary: str
    contradictions: List[str]
    remediation_plan: List[str]
    explanation: str

    # ==========================
    # SAR
    # ==========================
    sar: Dict[str, Any]

    # ==========================
    # Output
    # ==========================
    recommendations: List[str]
    citations: List[str]
    retrieved_sources: List[Dict[str, Any]]
    final_verdict: str

    # ==========================
    # Guardrails
    # ==========================
    verified: bool
    guardrail_report: Dict[str, Any]

    # ==========================
    # Execution
    # ==========================
    execution_log: List[Dict[str, Any]]


def build_initial_state(
    contract_text: str,
    sow_text: str = "",
    metadata: Dict[str, Any] = None,
) -> "GraphState":
    """
    Builds a fresh, fully-populated `GraphState` so every field a node
    might read already has a safe default, regardless of which subset
    of agents actually runs before it.
    """

    return {
        "contract_text": contract_text,
        "sow_text": sow_text,
        "metadata": metadata or {},

        "investigation_summary": "",
        "entities": [],
        "red_flags": [],

        "evidence": [],

        "compliance_findings": [],
        "privacy_findings": [],

        "risk_score": 0,
        "confidence": 0.0,
        "risk_analysis": "",
        "validated_findings": [],

        "reasoning_summary": "",
        "contradictions": [],
        "remediation_plan": [],
        "explanation": "",

        "sar": {},

        "recommendations": [],
        "citations": [],
        "retrieved_sources": [],
        "final_verdict": "",

        "verified": False,
        "guardrail_report": {},

        "execution_log": [],
    }