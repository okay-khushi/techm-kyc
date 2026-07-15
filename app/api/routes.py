from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import new_request_id, verify_api_key
from app.exceptions.agent_exception import AgentExecutionError
from app.orchestrator.executor import workflow_executor
from app.orchestrator.graph_visualizer import to_mermaid
from app.orchestrator.state import build_initial_state
from app.orchestrator.workflow import graph as full_analysis_graph
from app.schemas.api import AnalyzeRequest
from app.telemetry.execution_history import execution_history
from app.telemetry.metrics import metrics
from app.tools.evidence_lookup import evidence_lookup_tool
from app.utils.formatter import to_jsonable
from app.workflows.contract_review import contract_review_graph
from app.workflows.investigation import investigation_graph
from app.workflows.privacy_review import privacy_review_graph

router = APIRouter(
    prefix="/api/v1",
    tags=["Analysis"],
    dependencies=[Depends(verify_api_key)],
)


async def _run(graph, request: AnalyzeRequest):

    state = build_initial_state(
        contract_text=request.contract_text,
        sow_text=request.sow_text,
        metadata=request.metadata,
    )

    request_id = new_request_id()

    try:
        result = await workflow_executor.run(
            graph,
            state,
            config={"configurable": {"thread_id": request_id}},
        )

    except AgentExecutionError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return to_jsonable(result)


@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """
    Runs the full, end-to-end investigation pipeline: guardrails,
    investigation, evidence, compliance, privacy, risk, reasoning,
    contradiction, remediation, explainability, SAR, citations and the
    final orchestrator verdict.
    """

    return await _run(full_analysis_graph, request)


@router.post("/analyze/investigation")
async def analyze_investigation(request: AnalyzeRequest):
    """
    Lightweight investigation + evidence lookup only.
    """

    return await _run(investigation_graph, request)


@router.post("/analyze/contract-review")
async def analyze_contract_review(request: AnalyzeRequest):
    """
    Investigation + compliance + privacy, without risk scoring or SAR.
    """

    return await _run(contract_review_graph, request)


@router.post("/analyze/privacy-review")
async def analyze_privacy_review(request: AnalyzeRequest):
    """
    Investigation + privacy findings only.
    """

    return await _run(privacy_review_graph, request)


@router.get("/clients")
async def list_clients():
    """
    Known clients from the KYC reference data, for UI pickers (e.g.
    the dashboard's client dropdown) to select a client_id by name
    instead of typing one in blind.
    """

    return {"clients": to_jsonable(evidence_lookup_tool.list_clients())}


@router.get("/history")
async def list_history():
    return {"request_ids": execution_history.list_ids()}


@router.get("/history/{request_id}")
async def get_history(request_id: str):
    result = execution_history.get(request_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Unknown request id.")

    return to_jsonable(result)


@router.get("/graph")
async def get_graph():
    return {"mermaid": to_mermaid(full_analysis_graph)}


@router.get("/metrics")
async def get_metrics():
    return metrics.snapshot()
