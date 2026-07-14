from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.guardrails.evidence_validator import evidence_validator
from app.services.risk_service import risk_service
from app.tools.vector_search import vector_search_tool


class RiskAgent(BaseAgent):

    prompt_name = "risk"

    async def execute(self, state):

        # ------------------------------------
        # Least-Privilege Authorization
        # ------------------------------------
        self.authorize_tool("vector_search")

        reference_context = vector_search_tool.run(
            "risk assessment beneficial ownership PEP sanctions screening"
        )

        state.setdefault("retrieved_sources", []).extend(reference_context)

        # ------------------------------------
        # LLM Risk Analysis
        # ------------------------------------
        response = await self.invoke(
            {
                "investigation_summary": state["investigation_summary"],
                "evidence": state["evidence"],
                "compliance_findings": state["compliance_findings"],
                "privacy_findings": state["privacy_findings"],
                "metadata": state["metadata"],
                "reference_context": reference_context,
            }
        )

        # ------------------------------------
        # Rule-based Risk Calculation
        # ------------------------------------
        result = risk_service.calculate(
            metadata=state["metadata"],
            evidence=state["evidence"],
            compliance=state["compliance_findings"],
            privacy=state["privacy_findings"],
            red_flags=state["red_flags"]
        )

        state["risk_score"] = result["score"]
        state["confidence"] = result["confidence"]

        # Store AI explanation
        state["risk_analysis"] = response.content

        # Add recommendations
        state["recommendations"].extend(result["reasons"])

        # ------------------------------------
        # Evidence Validation
        # ------------------------------------
        validated = evidence_validator.validate(
            findings=state["compliance_findings"],
            evidence=state["evidence"]
        )

        state["validated_findings"] = validated

        # ------------------------------------
        # Execution Log
        # ------------------------------------
        state["execution_log"].append(
            {
                "agent": "Risk",
                "status": "completed",
                "risk_score": result["score"],
                "confidence": result["confidence"],
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return state


risk_agent = RiskAgent()