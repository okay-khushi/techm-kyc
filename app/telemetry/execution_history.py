import threading
import uuid
from collections import OrderedDict
from typing import Any, Dict, List, Optional

MAX_HISTORY = 200


class ExecutionHistoryStore:
    """
    In-memory store of recent graph executions, keyed by request id.
    """

    def __init__(self, max_history: int = MAX_HISTORY):
        self._lock = threading.Lock()
        self._store: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
        self._max_history = max_history

    def save(self, state: Dict[str, Any], request_id: Optional[str] = None) -> str:
        request_id = request_id or str(uuid.uuid4())

        with self._lock:
            self._store[request_id] = state
            self._store.move_to_end(request_id)

            while len(self._store) > self._max_history:
                self._store.popitem(last=False)

        return request_id

    def get(self, request_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(request_id)

    def list_ids(self) -> List[str]:
        return list(self._store.keys())


execution_history = ExecutionHistoryStore()
