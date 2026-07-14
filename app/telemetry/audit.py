import json
import threading
from pathlib import Path

from app.utils.constants import CACHE_DIR
from app.utils.helpers import utcnow_iso

AUDIT_LOG_PATH = CACHE_DIR / "audit_log.jsonl"


class AuditLogger:
    """
    Append-only audit trail of agent/tool actions and generated reports,
    for compliance traceability of the engine itself.
    """

    def __init__(self, path: Path = AUDIT_LOG_PATH):
        self.path = path
        self._lock = threading.Lock()

    def record(self, event_type: str, details: dict):
        entry = {
            "timestamp": utcnow_iso(),
            "event_type": event_type,
            "details": details,
        }

        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self._lock:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

        return entry


audit_logger = AuditLogger()
