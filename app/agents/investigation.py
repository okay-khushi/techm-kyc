import re
from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.tools.contract_search import contract_search_tool
from app.tools.evidence_lookup import evidence_lookup_tool
from app.tools.vector_search import vector_search_tool

ENTITY_PATTERN = re.compile(r"\b[A-Z][a-zA-Z&.,]+(?:\s+[A-Z][a-zA-Z&.,]+){0,2}\b")
MAX_ENTITIES = 10


def _extract_entities(text: str):
    seen = []

    for candidate in ENTITY_PATTERN.findall(text or ""):
        if candidate not in seen:
            seen.append(candidate)

    return seen[:MAX_ENTITIES]


class InvestigationAgent(BaseAgent):

    prompt_name = "investigation"

    async def execute(self, state):

        # Tool Authorization
        self.authorize_tool("contract_search")
        self.authorize_tool("evidence_lookup")
        self.authorize_tool("vector_search")

        entities = _extract_entities(state["contract_text"])

        key_sections = contract_search_tool.run(
            query="parties obligations sanctions risk termination",
            contract_text=state["contract_text"],
            sow_text=state["sow_text"],
        )

        evidence_hits = evidence_lookup_tool.run(entities, state["metadata"])

        reference_context = vector_search_tool.run(
            "high risk jurisdiction AML sanctions customer due diligence"
        )

        response = await self.invoke(
            {
                "contract_text": state["contract_text"],
                "sow_text": state["sow_text"],
                "metadata": state["metadata"],
                "key_sections": key_sections,
                "sanctions_matches": evidence_hits["sanctions_matches"],
            }
        )

        state["investigation_summary"] = response.content

        state["entities"] = [{"name": name} for name in entities]

        red_flags = []

        if evidence_hits["sanctions_matches"]:
            red_flags.append("Entity name matches a sanctions list.")

        for match in evidence_hits["kyc_matches"]:
            if match.get("sanctions_flag") or match.get("pep_flag"):
                red_flags.append(
                    f"KYC record flags {match.get('client_name', 'client')} "
                    "for sanctions/PEP risk."
                )
                break

        state["red_flags"] = red_flags

        state["recommendations"] = []

        state.setdefault("retrieved_sources", []).extend(reference_context)

        state["execution_log"].append(
            {
                "agent": "Investigation",
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return state


investigation_agent = InvestigationAgent()
