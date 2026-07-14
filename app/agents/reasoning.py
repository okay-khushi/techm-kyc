"""
Reasoning Agent

Responsibilities:
- Synthesize investigation, evidence, compliance, privacy and risk
  output into a single coherent narrative, without calling the LLM
  again (purely a deterministic aggregation step).
"""

from datetime import datetime

from app.agents.base_agent import BaseAgent


class ReasoningAgent(BaseAgent):

    async def execute(self, state):

        parts = [
            f"Investigation: {state['investigation_summary']}",
            f"Evidence collected: {len(state['evidence'])} item(s).",
            f"Compliance findings: {'; '.join(state['compliance_findings'])}",
            f"Privacy findings: {'; '.join(state['privacy_findings'])}",
            f"Risk score: {state['risk_score']} (confidence {state['confidence']}).",
            f"Risk analysis: {state['risk_analysis']}",
        ]

        state["reasoning_summary"] = "\n".join(parts)

        state["execution_log"].append(
            {
                "agent": "Reasoning",
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return state


reasoning_agent = ReasoningAgent()
