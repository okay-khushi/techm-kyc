"""
Privacy-focused review graph: investigation and privacy findings only.
"""

from langgraph.graph import END, START, StateGraph

from app.orchestrator.checkpoints import get_checkpointer
from app.orchestrator.nodes import NODES
from app.orchestrator.state import GraphState

builder = StateGraph(GraphState)

for name in ("guardrail", "investigation", "privacy", "citation"):
    builder.add_node(name, NODES[name])

builder.add_edge(START, "guardrail")
builder.add_edge("guardrail", "investigation")
builder.add_edge("investigation", "privacy")
builder.add_edge("privacy", "citation")
builder.add_edge("citation", END)

privacy_review_graph = builder.compile(checkpointer=get_checkpointer())
