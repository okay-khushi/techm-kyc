from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.services.privacy_service import privacy_service
from app.tools.gdpr_lookup import gdpr_lookup_tool
from app.tools.policy_lookup import policy_lookup_tool


class PrivacyAgent(BaseAgent):

    prompt_name = "privacy"

    async def execute(self, state):

        self.authorize_tool("gdpr_lookup")
        self.authorize_tool("policy_lookup")

        gdpr_context = gdpr_lookup_tool.run(state["contract_text"])
        policy_context = policy_lookup_tool.run(state["contract_text"], with_segments=True)

        response = await self.invoke(
            {
                "contract_text": state["contract_text"],
                "metadata": state["metadata"],
                "compliance": state["compliance_findings"],
                "gdpr_context": gdpr_context,
                "policy_context": policy_context,
            }
        )

        findings = privacy_service.analyze(
            contract_text=state["contract_text"],
            metadata=state["metadata"],
            compliance_findings=state["compliance_findings"]
        )

        findings.append(response.content)

        state["privacy_findings"] = findings

        state.setdefault("retrieved_sources", []).extend(gdpr_context + policy_context)

        state["execution_log"].append(
            {
                "agent": "Privacy",
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return state


privacy_agent = PrivacyAgent()
