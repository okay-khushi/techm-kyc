from typing import List

from pydantic import BaseModel

from app.utils.constants import RISK_LEVELS


class RiskAssessment(BaseModel):

    score: int
    confidence: float
    reasons: List[str] = []

    @property
    def level(self) -> str:
        for threshold, label in RISK_LEVELS:
            if self.score >= threshold:
                return label

        return "low"
