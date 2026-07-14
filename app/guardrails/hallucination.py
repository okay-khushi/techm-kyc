from typing import Dict, List


class HallucinationGuardrail:

    """
    Verifies AI output is grounded in available evidence.
    """

    def validate(
        self,
        llm_output: str,
        evidence: List[Dict]
    ) -> Dict:

        if not evidence:

            return {
                "verified": False,
                "reason": "No evidence available."
            }

        evidence_text = " ".join(
            str(item)
            for item in evidence
        ).lower()

        supported = 0

        for word in llm_output.lower().split():

            if word in evidence_text:
                supported += 1

        confidence = supported / max(
            len(llm_output.split()),
            1
        )

        return {

            "verified": confidence >= 0.20,

            "confidence": round(confidence, 2)
        }


hallucination_guardrail = HallucinationGuardrail()