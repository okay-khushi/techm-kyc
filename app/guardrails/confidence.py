from typing import Iterable

from app.utils.constants import DEFAULT_CONFIDENCE_THRESHOLD


class ConfidenceGuardrail:
    """
    Checks whether a confidence score (or the aggregate of several)
    clears the minimum bar required to trust a finding.
    """

    def check(self, confidence: float, threshold: float = DEFAULT_CONFIDENCE_THRESHOLD) -> bool:
        return confidence >= threshold

    def aggregate(self, scores: Iterable[float]) -> float:
        scores = list(scores)

        if not scores:
            return 0.0

        return round(sum(scores) / len(scores), 2)


confidence_guardrail = ConfidenceGuardrail()
