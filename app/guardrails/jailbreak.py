import re
from typing import Dict

JAILBREAK_PATTERNS = [
    r"\bdan\b",
    r"do anything now",
    r"no (restrictions|rules|limits) apply",
    r"pretend (you are|to be) (an? )?(unfiltered|uncensored|unrestricted)",
    r"jailbreak",
    r"bypass (your|the) (safety|guardrails|content policy)",
    r"without (any )?(ethical|moral) (guidelines|constraints)",
    r"hypothetically,? (how|what) would you",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in JAILBREAK_PATTERNS]


class JailbreakGuardrail:
    """
    Heuristic detector for jailbreak / role-play attempts intended to
    make the LLM ignore its safety and grounding rules.
    """

    def detect(self, text: str) -> Dict:
        if not text:
            return {"detected": False, "matches": []}

        matches = [
            pattern.pattern
            for pattern in COMPILED_PATTERNS
            if pattern.search(text)
        ]

        return {"detected": len(matches) > 0, "matches": matches}


jailbreak_guardrail = JailbreakGuardrail()
