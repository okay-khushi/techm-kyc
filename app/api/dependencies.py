import uuid

from fastapi import Header, HTTPException, status

from app.config.settings import settings


def get_settings():
    return settings


def new_request_id() -> str:
    return str(uuid.uuid4())


async def verify_api_key(x_api_key: str = Header(default=None)):
    """
    No-op unless `API_KEY` is configured, so the app remains easy to
    run locally without any auth setup.
    """

    if not settings.API_KEY:
        return

    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
