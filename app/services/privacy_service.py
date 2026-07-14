from typing import Dict, List


class PrivacyService:
    """
    Privacy Compliance Service

    Future:
    - GDPR lookup
    - PrivacyQA
    - OPP115
    """

    def analyze(
        self,
        contract_text: str,
        metadata: Dict,
        compliance_findings: List[str]
    ) -> List[str]:

        findings = []

        text = contract_text.lower()

        if "personal data" in text:
            findings.append(
                "Personal data detected."
            )

        if "consent" not in text:
            findings.append(
                "Consent clause not detected."
            )

        if "retention" not in text:
            findings.append(
                "Data retention policy missing."
            )

        if metadata.get("contains_pii", False):
            findings.append(
                "PII present. GDPR review recommended."
            )

        if len(compliance_findings):
            findings.append(
                "Privacy review aligned with compliance findings."
            )

        if len(findings) == 0:
            findings.append(
                "No privacy issues detected."
            )

        return findings


privacy_service = PrivacyService()