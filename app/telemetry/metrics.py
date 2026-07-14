import threading
from collections import defaultdict
from typing import Dict


class MetricsCollector:
    """
    Minimal in-process metrics collector: counters and timing samples.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._counters: Dict[str, int] = defaultdict(int)
        self._timings: Dict[str, list] = defaultdict(list)

    def increment(self, name: str, value: int = 1):
        with self._lock:
            self._counters[name] += value

    def record_timing(self, name: str, seconds: float):
        with self._lock:
            self._timings[name].append(seconds)

    def snapshot(self) -> Dict:
        with self._lock:
            return {
                "counters": dict(self._counters),
                "timings": {
                    name: {
                        "count": len(samples),
                        "avg": sum(samples) / len(samples) if samples else 0,
                        "max": max(samples) if samples else 0,
                    }
                    for name, samples in self._timings.items()
                },
            }


metrics = MetricsCollector()
