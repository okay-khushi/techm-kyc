"""
Remediation Agent

Responsibilities:
- Recommend remediation actions proportionate to the assessed risk
  level, using both a deterministic baseline and an LLM-assisted
  refinement.
"""

from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.models.risk import RiskAssessment

BASELINE_ACTIONS = {
    "critical": [
        "Escalate to compliance officer immediately.",
        "File a Suspicious Activity Report.",
        "Freeze or restrict the account pending review.",
    ],
    "high": [
        "Apply enhanced due diligence.",
        "Escalate to compliance officer.",
        "Request additional supporting documentation.",
    ],
    "medium": [
        "Apply standard due diligence review.",
        "Monitor account activity for further red flags.",
    ],
    "low": [
        "No immediate action required; continue standard monitoring.",
    ],
}


class RemediationAgent(BaseAgent):

    prompt_name = "remediation"

    async def execute(self, state):

        assessment = RiskAssessment(
            score=state["risk_score"],
            confidence=state["confidence"],
            reasons=state["recommendations"],
        )

        plan = list(BASELINE_ACTIONS.get(assessment.level, []))

        response = await self.invoke(
            {
                "investigation_summary": state["investigation_summary"],
                "risk_score": state["risk_score"],
                "risk_level": assessment.level,
                "compliance_findings": state["compliance_findings"],
                "privacy_findings": state["privacy_findings"],
            }
        )

        plan.append(response.content)

        state["remediation_plan"] = plan
        state["recommendations"].extend(BASELINE_ACTIONS.get(assessment.level, []))

        state["execution_log"].append(
            {
                "agent": "Remediation",
                "status": "completed",
                "risk_level": assessment.level,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return state


remediation_agent = RemediationAgent()
