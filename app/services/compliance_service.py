from typing import Dict, List


class ComplianceService:
    """
    Performs basic compliance checks.

    Later this will read:
    - GDPR
    - FATF
    - OFAC
    """

    def analyze(
        self,
        investigation_summary: str,
        metadata: Dict,
        evidence: List,
    ) -> List[str]:

        findings = []

        text = investigation_summary.lower()

        if "sanction" in text:
            findings.append(
                "Potential sanctions screening required."
            )

        if "pep" in text:
            findings.append(
                "Politically Exposed Person review required."
            )

        if len(evidence) == 0:
            findings.append(
                "No supporting evidence collected."
            )

        if metadata.get("country") in [
            "Iran",
            "North Korea",
            "Russia"
        ]:
            findings.append(
                "High-risk jurisdiction detected."
            )

        if len(findings) == 0:
            findings.append(
                "No major compliance violations detected."
            )

        return findings


compliance_service = ComplianceService()