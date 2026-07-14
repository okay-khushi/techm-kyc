import re

PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"\b\+?\d[\d\-\s()]{7,}\d\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
}


class PrivacyFilter:
    """
    Redacts common PII patterns from text before it is logged, cached,
    or otherwise persisted outside the immediate request.
    """

    def redact(self, text: str) -> str:
        if not text:
            return text

        redacted = text

        for label, pattern in PATTERNS.items():
            redacted = pattern.sub(f"[REDACTED_{label.upper()}]", redacted)

        return redacted

    def contains_pii(self, text: str) -> bool:
        if not text:
            return False

        return any(pattern.search(text) for pattern in PATTERNS.values())


privacy_filter = PrivacyFilter()
