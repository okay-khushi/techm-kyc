"""
The complete, end-to-end investigation pipeline. This is the canonical
graph also compiled in `app.orchestrator.workflow`; it is re-exported
here so all graphs live under a consistent `app.workflows` namespace.
"""

from app.orchestrator.workflow import graph as full_analysis_graph

__all__ = ["full_analysis_graph"]
