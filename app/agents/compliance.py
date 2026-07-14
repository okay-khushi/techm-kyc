from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.services.compliance_service import compliance_service
from app.tools.clause_lookup import clause_lookup_tool
from app.tools.gdpr_lookup import gdpr_lookup_tool
from app.tools.policy_lookup import policy_lookup_tool
from app.tools.regulation_lookup import regulation_lookup_tool


class ComplianceAgent(BaseAgent):

    prompt_name = "compliance"

    async def execute(self, state):

        self.authorize_tool("clause_lookup")
        self.authorize_tool("regulation_lookup")
        self.authorize_tool("gdpr_lookup")
        self.authorize_tool("policy_lookup")

        clauses = clause_lookup_tool.run(state["contract_text"])
        regulation_context = regulation_lookup_tool.run(state["investigation_summary"])
        gdpr_context = gdpr_lookup_tool.run(state["investigation_summary"])
        policy_context = policy_lookup_tool.run(state["investigation_summary"])

        response = await self.invoke(
            {
                "investigation": state["investigation_summary"],
                "evidence": state["evidence"],
                "metadata": state["metadata"],
                "clauses": clauses,
                "regulation_context": regulation_context,
                "gdpr_context": gdpr_context,
            }
        )

        findings = compliance_service.analyze(
            investigation_summary=state["investigation_summary"],
            metadata=state["metadata"],
            evidence=state["evidence"]
        )

        findings.append(response.content)

        state["compliance_findings"] = findings

        state.setdefault("retrieved_sources", []).extend(
            regulation_context + gdpr_context + policy_context
        )

        state["execution_log"].append(
            {
                "agent": "Compliance",
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return state


compliance_agent = ComplianceAgent()
