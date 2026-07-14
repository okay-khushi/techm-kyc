"""
Contradiction Agent

Responsibilities:
- Detect inconsistencies between the risk score and the
  compliance/privacy findings (e.g. "no violations" alongside a high
  risk score), purely through rule-based checks.
"""

from datetime import datetime

from app.agents.base_agent import BaseAgent

NO_ISSUE_PHRASES = [
    "no major compliance violations detected",
    "no privacy issues detected",
]

HIGH_RISK_THRESHOLD = 50


class ContradictionAgent(BaseAgent):

    async def execute(self, state):

        contradictions = []

        findings_text = " ".join(
            state["compliance_findings"] + state["privacy_findings"]
        ).lower()

        no_issues_reported = any(
            phrase in findings_text for phrase in NO_ISSUE_PHRASES
        )

        if state["risk_score"] >= HIGH_RISK_THRESHOLD and no_issues_reported:
            contradictions.append(
                "Risk score is high but compliance/privacy findings report no "
                "issues. Findings may be incomplete."
            )

        if state["risk_score"] < 25 and len(state["red_flags"]) > 0:
            contradictions.append(
                "Risk score is low despite red flags being present during "
                "investigation."
            )

        if state["evidence"] and not state["validated_findings"]:
            contradictions.append(
                "Evidence was collected but no findings were validated against it."
            )

        state["contradictions"] = contradictions

        state["execution_log"].append(
            {
                "agent": "Contradiction",
                "status": "completed",
                "contradictions_found": len(contradictions),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return state


contradiction_agent = ContradictionAgent()
