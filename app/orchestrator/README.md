# Orchestrator

- `state.py` — the shared `GraphState` TypedDict and
  `build_initial_state()` factory.
- `nodes.py` — single registry mapping node name -> agent `execute`
  coroutine, shared by every graph under `app/workflows`.
- `router.py` — conditional-edge functions (e.g. `route_privacy`).
- `workflow.py` — compiles the canonical full-pipeline graph
  (re-exported as `app.workflows.full_analysis.full_analysis_graph`).
- `checkpoints.py` — process-wide `MemorySaver`, so graphs are
  resumable/replayable by `thread_id`.
- `executor.py` — `WorkflowExecutor` wraps `graph.ainvoke` with
  tracing, audit logging and execution-history persistence.
- `events.py` — `stream_events()` turns `graph.astream` into
  per-node `StepEvent`s for progress reporting.
- `graph_visualizer.py` — renders the compiled graph as mermaid/PNG.

Every compiled graph requires a `thread_id` in
`config["configurable"]` at invocation time, since a checkpointer is
always attached.
