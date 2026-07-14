import time
from contextlib import contextmanager
from typing import Dict, List

from app.telemetry.metrics import metrics


class TraceRecorder:
    """
    Records durations of named steps (e.g. agent/tool execution) for a
    single request, in call order.
    """

    def __init__(self):
        self.spans: List[Dict] = []

    @contextmanager
    def span(self, name: str):
        start = time.perf_counter()

        try:
            yield
        finally:
            duration = time.perf_counter() - start

            self.spans.append({"name": name, "duration": duration})
            metrics.record_timing(name, duration)

    def as_list(self) -> List[Dict]:
        return list(self.spans)
