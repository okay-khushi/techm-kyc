"""
SAR Agent

Responsibilities:
- Generate Suspicious Activity Report
- Validate AI output against evidence
- Store final report
"""

from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.guardrails.hallucination import hallucination_guardrail
from app.services.report_service import report_service


class SARAgent(BaseAgent):

    prompt_name = "sar"

    async def execute(self, state):

        # Generate AI SAR
        response = await self.invoke(
            {
                "investigation_summary": state["investigation_summary"],
                "evidence": state["evidence"],
                "compliance_findings": state["compliance_findings"],
                "privacy_findings": state["privacy_findings"],
                "risk_score": state["risk_score"],
                "recommendations": state["recommendations"]
            }
        )

        # Build base SAR report
        report = report_service.generate(state)

        report["llm_summary"] = response.content

        # -----------------------------
        # Hallucination Verification
        # -----------------------------
        verification = hallucination_guardrail.validate(
            llm_output=response.content,
            evidence=state["evidence"]
        )

        report["verification"] = verification

        state["verified"] = verification["verified"]

        # Store SAR
        state["sar"] = report

        # Execution log
        state["execution_log"].append(
            {
                "agent": "SAR",
                "status": "completed",
                "verified": verification["verified"],
                "confidence": verification["confidence"],
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return state


sar_agent = SARAgent()