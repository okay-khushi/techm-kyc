from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.tools.evidence_lookup import evidence_lookup_tool
from app.tools.vector_search import vector_search_tool


class EvidenceAgent(BaseAgent):

    prompt_name = "evidence"

    async def execute(self, state):

        self.authorize_tool("evidence_lookup")
        self.authorize_tool("vector_search")

        entity_names = [entity.get("name") for entity in state["entities"]]

        hits = evidence_lookup_tool.run(entity_names, state["metadata"])

        reference_context = vector_search_tool.run(
            "suspicious activity indicators money laundering red flags"
        )

        response = await self.invoke(
            {
                "investigation": state["investigation_summary"],
                "entities": state["entities"],
                "red_flags": state["red_flags"],
                "sanctions_matches": hits["sanctions_matches"],
                "kyc_matches": hits["kyc_matches"],
            }
        )

        evidence = [
            {
                "type": "AI",
                "description": response.content
            }
        ]

        for match in hits["sanctions_matches"]:
            evidence.append({
                "type": "sanctions_match",
                "description": f"{match.get('name')} matched in {match.get('source')}.",
                "source": match.get("source"),
            })

        for match in hits["kyc_matches"]:
            evidence.append({
                "type": "kyc_record",
                "description": f"KYC record for {match.get('client_name', 'client')} from {match.get('source')}.",
                "source": match.get("source"),
            })

        for match in hits["transaction_matches"]:
            evidence.append({
                "type": "transaction_record",
                "description": f"Transaction {match.get('transaction_id')} of {match.get('amount')} "
                               f"between {match.get('client_country')} and {match.get('counterparty_country')}.",
                "source": "transactions_with_fatf_ofac",
            })

        state["evidence"] = evidence

        state.setdefault("retrieved_sources", []).extend(reference_context)

        state["execution_log"].append(
            {
                "agent": "Evidence",
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return state


evidence_agent = EvidenceAgent()
