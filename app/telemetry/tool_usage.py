from datetime import datetime


class ToolLogger:

    def log(
        self,
        agent,
        tool
    ):

        print(
            f"[{datetime.utcnow()}] "
            f"{agent} used {tool}"
        )


tool_logger = ToolLogger()
