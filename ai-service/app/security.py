from fastapi import Header, HTTPException, status

from app.config import settings


async def verify_internal_api_key(x_internal_api_key: str | None = Header(default=None)):
    """If AI_INTERNAL_API_KEY is configured, require callers (the Java
    backend) to present it. Left open in local development when unset so
    the service is easy to run out of the box."""
    if not settings.internal_api_key:
        return
    if x_internal_api_key != settings.internal_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing internal API key")
