"""
Citation Agent

Responsibilities:
- Build the final citation trail from evidence, compliance/privacy
  findings, and any knowledge-base sources retrieved during the run.
"""

from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.services.citation_service import citation_service


class CitationAgent(BaseAgent):

    async def execute(self, state):

        state["citations"] = citation_service.build_citations(
            evidence=state["evidence"],
            compliance_findings=state["compliance_findings"],
            privacy_findings=state["privacy_findings"],
            retrieved_sources=state.get("retrieved_sources", []),
        )

        state["execution_log"].append(
            {
                "agent": "Citation",
                "status": "completed",
                "citation_count": len(state["citations"]),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return state


citation_agent = CitationAgent()
