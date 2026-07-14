from typing import Any, Dict, List

import numpy as np


def to_jsonable(value: Any) -> Any:
    """
    Recursively converts numpy/pandas scalar types coming out of tool
    lookups (numpy int64/float64/bool_, ndarrays, NaN) into plain
    JSON-serializable Python types, so API responses never crash on a
    stray pandas value.
    """

    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]

    if isinstance(value, np.ndarray):
        return to_jsonable(value.tolist())

    if isinstance(value, np.generic):
        item = value.item()

        return None if isinstance(item, float) and item != item else item

    if isinstance(value, float) and value != value:
        return None

    return value


def format_percentage(value: float) -> str:
    return f"{value * 100:.1f}%"


def format_currency(amount: float, currency: str = "USD") -> str:
    return f"{amount:,.2f} {currency}"


def format_findings_list(findings: List[str]) -> str:
    if not findings:
        return "- None identified."

    return "\n".join(f"- {finding}" for finding in findings)


def format_report_markdown(report: Dict[str, Any]) -> str:
    """
    Renders a generated SAR report dict as a human-readable markdown document.
    """

    lines = [
        "# Suspicious Activity Report",
        "",
        f"**Generated At:** {report.get('generated_at', '')}",
        f"**Risk Score:** {report.get('risk_score', 0)}",
        f"**Confidence:** {format_percentage(report.get('confidence', 0.0))}",
        "",
        "## Executive Summary",
        report.get("llm_summary", "") or report.get("summary", ""),
        "",
        "## Investigation Summary",
        report.get("summary", ""),
        "",
        "## Compliance Findings",
        format_findings_list(report.get("compliance_findings", [])),
        "",
        "## Privacy Findings",
        format_findings_list(report.get("privacy_findings", [])),
        "",
        "## Recommendations",
        format_findings_list(report.get("recommendations", [])),
    ]

    verification = report.get("verification")

    if verification:
        lines += [
            "",
            "## Verification",
            f"- Verified: {verification.get('verified')}",
            f"- Confidence: {verification.get('confidence', 0)}",
        ]

    return "\n".join(lines)
