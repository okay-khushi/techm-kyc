from typing import Any, Dict

from app.exceptions.agent_exception import AgentExecutionError
from app.telemetry.audit import audit_logger
from app.telemetry.execution_history import execution_history
from app.telemetry.traces import TraceRecorder


class WorkflowExecutor:
    """
    Runs a compiled LangGraph graph with tracing, audit logging and
    execution-history persistence around it, translating unexpected
    failures into `AgentExecutionError`.
    """

    async def run(self, graph, initial_state: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:

        trace = TraceRecorder()

        try:
            with trace.span("graph_execution"):
                final_state = await graph.ainvoke(initial_state, config=config)

        except Exception as exc:
            audit_logger.record("workflow_failed", {"error": str(exc)})

            raise AgentExecutionError("Workflow", str(exc)) from exc

        request_id = execution_history.save(final_state)

        audit_logger.record(
            "workflow_completed",
            {
                "request_id": request_id,
                "risk_score": final_state.get("risk_score"),
                "verified": final_state.get("verified"),
            },
        )

        final_state["request_id"] = request_id
        final_state["trace"] = trace.as_list()

        return final_state


workflow_executor = WorkflowExecutor()
