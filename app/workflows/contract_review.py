"""
Contract-focused review graph: investigation, compliance and privacy
findings without risk scoring or SAR generation.
"""

from langgraph.graph import END, START, StateGraph

from app.orchestrator.checkpoints import get_checkpointer
from app.orchestrator.nodes import NODES
from app.orchestrator.router import route_privacy
from app.orchestrator.state import GraphState

builder = StateGraph(GraphState)

for name in ("guardrail", "investigation", "evidence", "compliance", "privacy", "citation"):
    builder.add_node(name, NODES[name])

builder.add_edge(START, "guardrail")
builder.add_edge("guardrail", "investigation")
builder.add_edge("investigation", "evidence")
builder.add_edge("evidence", "compliance")

builder.add_conditional_edges(
    "compliance",
    route_privacy,
    {"privacy": "privacy", "risk": "citation"},
)

builder.add_edge("privacy", "citation")
builder.add_edge("citation", END)

contract_review_graph = builder.compile(checkpointer=get_checkpointer())
