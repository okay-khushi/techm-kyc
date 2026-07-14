from langgraph.graph import StateGraph, START, END

from app.orchestrator.checkpoints import get_checkpointer
from app.orchestrator.nodes import NODES
from app.orchestrator.router import route_privacy
from app.orchestrator.state import GraphState

builder = StateGraph(GraphState)

for name, node in NODES.items():
    builder.add_node(name, node)

builder.add_edge(START, "guardrail")
builder.add_edge("guardrail", "investigation")
builder.add_edge("investigation", "evidence")
builder.add_edge("evidence", "compliance")

builder.add_conditional_edges(
    "compliance",
    route_privacy,
    {"privacy": "privacy", "risk": "risk"},
)

builder.add_edge("privacy", "risk")
builder.add_edge("risk", "reasoning")
builder.add_edge("reasoning", "contradiction")
builder.add_edge("contradiction", "remediation")
builder.add_edge("remediation", "explainability")
builder.add_edge("explainability", "sar")
builder.add_edge("sar", "citation")
builder.add_edge("citation", "orchestrator")
builder.add_edge("orchestrator", END)

graph = builder.compile(checkpointer=get_checkpointer())