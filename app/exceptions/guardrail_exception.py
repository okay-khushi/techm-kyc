class GuardrailViolationError(Exception):
    """
    Raised when a guardrail blocks execution (e.g. jailbreak or
    prompt-injection attempt, unverified hallucinated output).
    """

    def __init__(self, guardrail: str, reason: str):
        self.guardrail = guardrail
        self.reason = reason

        super().__init__(f"[{guardrail}] blocked: {reason}")
