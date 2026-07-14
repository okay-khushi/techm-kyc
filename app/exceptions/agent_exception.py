class AgentExecutionError(Exception):
    """
    Raised when an agent fails to complete its execution step.
    """

    def __init__(self, agent: str, message: str):
        self.agent = agent
        self.message = message

        super().__init__(f"[{agent}] {message}")
