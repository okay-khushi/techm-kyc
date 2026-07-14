from typing import Dict, List

from app.utils.constants import MIN_OUTPUT_LENGTH

REFUSAL_PATTERNS = [
    "i cannot help with that",
    "i can't help with that",
    "as an ai language model",
    "i'm not able to assist",
]


class OutputValidator:
    """
    Sanity-checks raw LLM output before it is trusted by downstream
    agents: non-empty, long enough, and not a refusal/deflection.
    """

    def validate(self, output: str) -> Dict:
        reasons: List[str] = []

        if not output or not output.strip():
            reasons.append("Empty output.")

        elif len(output.strip()) < MIN_OUTPUT_LENGTH:
            reasons.append("Output too short.")

        lowered = (output or "").lower()

        if any(pattern in lowered for pattern in REFUSAL_PATTERNS):
            reasons.append("Output looks like a refusal/deflection.")

        return {"valid": len(reasons) == 0, "reasons": reasons}


output_validator = OutputValidator()
