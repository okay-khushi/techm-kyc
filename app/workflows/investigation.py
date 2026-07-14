"""
Lightweight graph for quick entity/evidence lookups, without
compliance, privacy, risk scoring or SAR generation.
"""

from langgraph.graph import END, START, StateGraph

from app.orchestrator.checkpoints import get_checkpointer
from app.orchestrator.nodes import NODES
from app.orchestrator.state import GraphState

builder = StateGraph(GraphState)

for name in ("guardrail", "investigation", "evidence"):
    builder.add_node(name, NODES[name])

builder.add_edge(START, "guardrail")
builder.add_edge("guardrail", "investigation")
builder.add_edge("investigation", "evidence")
builder.add_edge("evidence", END)

investigation_graph = builder.compile(checkpointer=get_checkpointer())
