"""
Least Privilege Guardrail
"""

from app.tools.tool_permissions import tool_permissions


class LeastPrivilegeGuardrail:

    def check(
        self,
        agent: str,
        tool: str
    ) -> bool:

        allowed = tool_permissions.allowed_tools(
            agent
        )

        return tool in allowed


least_privilege_guardrail = (
    LeastPrivilegeGuardrail()
)