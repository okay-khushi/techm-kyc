from abc import ABC, abstractmethod

from app.guardrails.least_privilege import (
    least_privilege_guardrail,
)
from app.services.llm_service import get_llm
from app.telemetry.tool_usage import tool_logger
from app.utils.prompt_loader import load_prompt


class BaseAgent(ABC):
    """
    Base class for all AI Agents.
    """

    prompt_name = ""

    async def invoke(self, state):

        llm = get_llm()

        prompt = load_prompt(self.prompt_name)

        response = await llm.ainvoke(
            f"""
{prompt}

Input:
{state}
"""
        )

        return response

    def authorize_tool(self, tool_name: str):
        """
        Ensures the current agent is allowed to use a tool.
        """

        agent = self.__class__.__name__.replace(
            "Agent",
            ""
        )

        allowed = least_privilege_guardrail.check(
            agent,
            tool_name
        )

        if not allowed:
            raise PermissionError(
                f"{agent} is not allowed to use '{tool_name}'"
            )

        tool_logger.log(
            agent,
            tool_name
        )

        return True

    @abstractmethod
    async def execute(self, state):
        pass