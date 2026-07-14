import re
from typing import Dict

PROMPT_INJECTION_PATTERNS = [
    r"ignore (all|any|the) (previous|prior|above) instructions",
    r"disregard (all|any|the) (previous|prior|above)",
    r"you are now",
    r"new instructions?:",
    r"system prompt",
    r"reveal (your|the) (system|hidden) prompt",
    r"act as (if|though)",
    r"forget (everything|all) (you were told|above)",
    r"override (your|the) (rules|instructions|guardrails)",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in PROMPT_INJECTION_PATTERNS]


class PromptInjectionGuardrail:
    """
    Heuristic detector for prompt-injection attempts embedded in
    untrusted input (contract/SOW text) before it reaches the LLM.
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


prompt_injection_guardrail = PromptInjectionGuardrail()
