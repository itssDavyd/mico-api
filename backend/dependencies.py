from fastapi import Request

from config import get_settings
from routers.auth import verify_session


async def optional_auth(request: Request) -> None:
    if get_settings().auth_enabled:
        verify_session(request)
