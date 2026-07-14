"""
Guardrail Agent

Responsibilities:
- Screen raw input (contract/SOW text) for jailbreak and
  prompt-injection attempts before any other agent processes it.
"""

from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.guardrails.jailbreak import jailbreak_guardrail
from app.guardrails.prompt_injection import prompt_injection_guardrail
from app.telemetry.audit import audit_logger


class GuardrailAgent(BaseAgent):

    prompt_name = "guardrail"

    async def execute(self, state):

        text = f"{state['contract_text']}\n{state['sow_text']}"

        jailbreak_result = jailbreak_guardrail.detect(text)
        injection_result = prompt_injection_guardrail.detect(text)

        flagged = jailbreak_result["detected"] or injection_result["detected"]

        assessment = ""

        if flagged:
            response = await self.invoke(
                {
                    "contract_text": state["contract_text"],
                    "sow_text": state["sow_text"],
                }
            )

            assessment = response.content

            state["recommendations"].append(
                "Input flagged for potential prompt injection / jailbreak attempt. "
                "Manual review recommended."
            )

            audit_logger.record(
                "guardrail_input_flagged",
                {
                    "jailbreak": jailbreak_result,
                    "prompt_injection": injection_result,
                },
            )

        state["guardrail_report"] = {
            "input": {
                "flagged": flagged,
                "jailbreak": jailbreak_result,
                "prompt_injection": injection_result,
                "assessment": assessment,
            }
        }

        state["execution_log"].append(
            {
                "agent": "Guardrail",
                "status": "completed",
                "flagged": flagged,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return state


guardrail_agent = GuardrailAgent()
