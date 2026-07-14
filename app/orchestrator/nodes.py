"""
Central registry of graph nodes: maps a node name to the agent
`execute` coroutine that runs for it. Used by `orchestrator.workflow`
and the alternate graphs under `app.workflows` so every graph builder
shares one source of truth instead of re-importing agents directly.
"""

from app.agents.citation import citation_agent
from app.agents.compliance import compliance_agent
from app.agents.contradiction import contradiction_agent
from app.agents.evidence import evidence_agent
from app.agents.explainability import explainability_agent
from app.agents.guardrail import guardrail_agent
from app.agents.investigation import investigation_agent
from app.agents.orchestrator import orchestrator_agent
from app.agents.privacy import privacy_agent
from app.agents.remediation import remediation_agent
from app.agents.reasoning import reasoning_agent
from app.agents.risk import risk_agent
from app.agents.sar import sar_agent

NODES = {
    "guardrail": guardrail_agent.execute,
    "investigation": investigation_agent.execute,
    "evidence": evidence_agent.execute,
    "compliance": compliance_agent.execute,
    "privacy": privacy_agent.execute,
    "risk": risk_agent.execute,
    "reasoning": reasoning_agent.execute,
    "contradiction": contradiction_agent.execute,
    "remediation": remediation_agent.execute,
    "explainability": explainability_agent.execute,
    "sar": sar_agent.execute,
    "citation": citation_agent.execute,
    "orchestrator": orchestrator_agent.execute,
}

# Canonical order for the full, end-to-end analysis pipeline.
FULL_PIPELINE_ORDER = [
    "guardrail",
    "investigation",
    "evidence",
    "compliance",
    "privacy",
    "risk",
    "reasoning",
    "contradiction",
    "remediation",
    "explainability",
    "sar",
    "citation",
    "orchestrator",
]
