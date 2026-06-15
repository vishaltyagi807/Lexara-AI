from __future__ import annotations
from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthException, ForbiddenException
from app.core.security import decode_token
from app.db.session import get_db

_bearer_scheme = HTTPBearer(auto_error=False)




def _extract_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
) -> str:
    token = request.headers.get("X-Access-Token")
    if not token:
        token = request.cookies.get("access_token")
    if not token and credentials and credentials.credentials:
        token = credentials.credentials

    if not token:
        raise AuthException(
            detail="Authentication token missing or malformed.",
            code="MISSING_TOKEN",
        )

    payload = decode_token(token)
    if payload.get("token_type") != "access":
        raise AuthException(
            detail="Invalid token type. Only access tokens are allowed.",
            code="INVALID_TOKEN_TYPE",
        )
    return token



async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ] = None,
) -> "User":
    from app.models.user import User
    from app.services.auth_service import get_current_user as svc_get_current_user

    token = _extract_token(request, credentials)

    import redis.asyncio as aioredis

    redis_client: aioredis.Redis = aioredis.from_url(
        settings.REDIS_URL, decode_responses=True
    )
    async with redis_client:
        is_blacklisted = await redis_client.get(f"blacklist:{token}")
        if is_blacklisted:
            raise AuthException(detail="Token has been revoked.", code="TOKEN_REVOKED")

    user = await svc_get_current_user(db=db, token=token)
    return user




async def get_current_active_user(
    current_user: Annotated["User", Depends(get_current_user)],
) -> "User":
    if not current_user.is_active:
        raise ForbiddenException(
            detail="This account has been deactivated.",
            code="ACCOUNT_INACTIVE",
        )
    return current_user



_TIER_ORDER = {"free": 0, "pro": 1, "enterprise": 2}


def require_tier(minimum_tier: str):
    async def _dependency(
        current_user: Annotated["User", Depends(get_current_active_user)],
    ) -> "User":
        user_tier_level = _TIER_ORDER.get(current_user.tier, 0)
        required_level = _TIER_ORDER.get(minimum_tier, 0)
        if user_tier_level < required_level:
            raise ForbiddenException(
                detail=f"This feature requires the '{minimum_tier}' tier or above.",
                code="INSUFFICIENT_TIER",
            )
        return current_user

    return _dependency
