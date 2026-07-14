import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.telemetry.logger import get_logger
from app.telemetry.metrics import metrics

logger = get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs method/path/status/duration for every request and records
    timing into the process-wide metrics collector.
    """

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()

        response = await call_next(request)

        duration = time.perf_counter() - start

        metrics.record_timing(f"http.{request.method}.{request.url.path}", duration)

        logger.info(
            f"{request.method} {request.url.path} "
            f"-> {response.status_code} ({duration:.3f}s)"
        )

        return response
