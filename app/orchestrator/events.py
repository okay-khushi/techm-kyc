from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict

from app.utils.helpers import utcnow_iso


@dataclass
class StepEvent:
    node: str
    status: str
    timestamp: str = field(default_factory=utcnow_iso)


async def stream_events(graph, state: Dict[str, Any]) -> AsyncIterator[StepEvent]:
    """
    Wraps `graph.astream` to yield a `StepEvent` per completed node,
    for progress-reporting/streaming API consumers.
    """

    async for update in graph.astream(state):
        for node_name in update.keys():
            yield StepEvent(node=node_name, status="completed")
