"""
Callable tool registry, keyed by the same tool names used in
`app.tools.tool_permissions` (the source of truth for *which* agent may
use *which* tool). This registry maps each name to the actual callable
so agents/tests can look tools up dynamically instead of importing
every tool module directly.
"""

from app.tools.clause_lookup import clause_lookup_tool
from app.tools.contract_search import contract_search_tool
from app.tools.evidence_lookup import evidence_lookup_tool
from app.tools.gdpr_lookup import gdpr_lookup_tool
from app.tools.policy_lookup import policy_lookup_tool
from app.tools.regulation_lookup import regulation_lookup_tool
from app.tools.vector_search import vector_search_tool

TOOLS = {
    "clause_lookup": clause_lookup_tool.run,
    "contract_search": contract_search_tool.run,
    "evidence_lookup": evidence_lookup_tool.run,
    "gdpr_lookup": gdpr_lookup_tool.run,
    "policy_lookup": policy_lookup_tool.run,
    "regulation_lookup": regulation_lookup_tool.run,
    "vector_search": vector_search_tool.run,
}