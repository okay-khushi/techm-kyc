"""
Explainability Agent

Responsibilities:
- Produce a plain-language explanation of how the final risk score was
  derived, purely from the reasons already collected (no LLM call, so
  the explanation can never introduce ungrounded claims).
"""

from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.models.risk import RiskAssessment


class ExplainabilityAgent(BaseAgent):

    async def execute(self, state):

        assessment = RiskAssessment(
            score=state["risk_score"],
            confidence=state["confidence"],
            reasons=[r for r in state["recommendations"] if r],
        )

        reason_text = (
            "; ".join(assessment.reasons)
            if assessment.reasons
            else "no specific risk factors were triggered"
        )

        explanation = (
            f"The overall risk score is {assessment.score}/100 "
            f"({assessment.level} risk), with {assessment.confidence * 100:.0f}% "
            f"confidence. This is driven by: {reason_text}."
        )

        if state["contradictions"]:
            explanation += (
                " Note: "
                + " ".join(state["contradictions"])
            )

        state["explanation"] = explanation

        state["execution_log"].append(
            {
                "agent": "Explainability",
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return state


explainability_agent = ExplainabilityAgent()
