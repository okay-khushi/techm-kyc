"""
Orchestrator Agent

Responsibilities:
- Run last, after every other agent, and produce a short executive
  verdict for the whole investigation.
- Run the final output-stage guardrails (output validation, PII
  redaction check, confidence threshold) over the generated report.
"""

from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.guardrails.confidence import confidence_guardrail
from app.guardrails.output_validator import output_validator
from app.guardrails.privacy_filter import privacy_filter


class OrchestratorAgent(BaseAgent):

    prompt_name = "orchestrator"

    async def execute(self, state):

        response = await self.invoke(
            {
                "investigation_summary": state["investigation_summary"],
                "evidence": state["evidence"],
                "compliance_findings": state["compliance_findings"],
                "privacy_findings": state["privacy_findings"],
                "risk_score": state["risk_score"],
                "explanation": state["explanation"],
                "remediation_plan": state["remediation_plan"],
                "contradictions": state["contradictions"],
            }
        )

        state["final_verdict"] = response.content

        llm_summary = state["sar"].get("llm_summary", "")

        output_check = output_validator.validate(llm_summary)
        pii_detected = privacy_filter.contains_pii(llm_summary)
        confidence_ok = confidence_guardrail.check(state["confidence"])

        guardrail_report = state.get("guardrail_report", {})
        guardrail_report["output"] = {
            "valid": output_check["valid"],
            "reasons": output_check["reasons"],
            "pii_detected": pii_detected,
            "confidence_ok": confidence_ok,
        }
        state["guardrail_report"] = guardrail_report

        state["execution_log"].append(
            {
                "agent": "Orchestrator",
                "status": "completed",
                "output_valid": output_check["valid"],
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return state


orchestrator_agent = OrchestratorAgent()
