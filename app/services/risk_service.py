from typing import Dict, List


class RiskService:
    """
    Calculates overall investigation risk score.
    """

    def calculate(
        self,
        metadata: Dict,
        evidence: List,
        compliance: List,
        privacy: List,
        red_flags: List,
    ) -> Dict:

        score = 0
        reasons = []

        # High-risk country
        if metadata.get("country") in [
            "Iran",
            "North Korea",
            "Russia"
        ]:
            score += 30
            reasons.append("High-risk jurisdiction")

        # Politically Exposed Person
        if metadata.get("pep", False):
            score += 25
            reasons.append("PEP detected")

        # Sanctions
        if metadata.get("sanctioned", False):
            score += 40
            reasons.append("Sanctioned entity")

        # Ownership opacity
        opacity = metadata.get("ownership_opacity", 0)

        if opacity > 70:
            score += 20
            reasons.append("Opaque ownership")

        # Red Flags
        score += len(red_flags) * 5

        # Evidence
        score += len(evidence) * 2

        # Compliance Findings
        score += len(compliance) * 3

        # Privacy Findings
        score += len(privacy)

        score = min(score, 100)

        confidence = round(
            min(
                0.5 + score / 200,
                0.99
            ),
            2
        )

        return {
            "score": score,
            "confidence": confidence,
            "reasons": reasons
        }


risk_service = RiskService()