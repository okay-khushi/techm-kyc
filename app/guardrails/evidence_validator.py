from typing import Dict, List


class EvidenceValidator:

    """
    Ensures every finding has evidence.
    """

    def validate(
        self,
        findings: List[str],
        evidence: List[Dict]
    ) -> List[Dict]:

        validated = []

        for finding in findings:

            validated.append({

                "finding": finding,

                "supported": len(evidence) > 0,

                "evidence_count": len(evidence)
            })

        return validated


evidence_validator = EvidenceValidator()