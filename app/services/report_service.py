from datetime import datetime
from typing import Dict


class ReportService:

    def generate(self, state) -> Dict:

        return {

            "generated_at": datetime.utcnow().isoformat(),

            "summary": state["investigation_summary"],

            "risk_score": state["risk_score"],

            "confidence": state["confidence"],

            "compliance_findings":
                state["compliance_findings"],

            "privacy_findings":
                state["privacy_findings"],

            "evidence":
                state["evidence"],

            "recommendations":
                state["recommendations"],

            "citations":
                state["citations"]
        }


report_service = ReportService()