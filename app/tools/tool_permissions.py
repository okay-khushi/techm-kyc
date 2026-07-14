"""
Tool Permission Registry

Defines which tools each AI agent is allowed to use.
"""

from typing import Dict, List


class ToolPermissionRegistry:

    def __init__(self):

        self.permissions: Dict[str, List[str]] = {

            "Investigation": [
                "contract_search",
                "evidence_lookup",
                "vector_search"
            ],

            "Evidence": [
                "evidence_lookup",
                "vector_search"
            ],

            "Compliance": [
                "clause_lookup",
                "regulation_lookup",
                "gdpr_lookup",
                "policy_lookup"
            ],

            "Privacy": [
                "gdpr_lookup",
                "policy_lookup"
            ],

            "Risk": [
                "vector_search"
            ],

            "SAR": []
        }

    def allowed_tools(
        self,
        agent_name: str
    ) -> List[str]:

        return self.permissions.get(
            agent_name,
            []
        )


tool_permissions = ToolPermissionRegistry()