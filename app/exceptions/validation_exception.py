class RequestValidationError(Exception):
    """
    Raised when an incoming API request fails domain-level validation
    (distinct from pydantic's own schema validation).
    """

    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason

        super().__init__(f"'{field}': {reason}")
