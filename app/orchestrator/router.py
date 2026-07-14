"""
Conditional routing functions for `add_conditional_edges`. Kept
separate from `nodes.py` so branching logic can be unit-tested and
reused across the different workflow graphs.
"""

from app.utils.helpers import contains_any


def route_privacy(state) -> str:
    """
    Skip the privacy agent when nothing suggests personal data is
    involved, to avoid a needless LLM call and false-positive findings.
    """

    metadata = state.get("metadata", {})

    if metadata.get("contains_pii"):
        return "privacy"

    if contains_any(state.get("contract_text", ""), ["personal data", "pii", "data subject"]):
        return "privacy"

    return "risk"
