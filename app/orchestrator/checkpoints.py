from langgraph.checkpoint.memory import MemorySaver

_checkpointer = None


def get_checkpointer() -> MemorySaver:
    """
    Returns a process-wide in-memory checkpointer, enabling graphs to
    be resumed/replayed by thread_id within a single running process.
    """

    global _checkpointer

    if _checkpointer is None:
        _checkpointer = MemorySaver()

    return _checkpointer
