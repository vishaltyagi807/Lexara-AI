from __future__ import annotations
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Header, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.core.exceptions import OAuthException
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ConnectedProvider,
    OAuthLoginResponse,
    PKCEAuthorizeRequest,
)
from app.services import oauth_service

router = APIRouter(prefix="/api/v1/auth/oauth", tags=["OAuth"])


async def get_redis():
    client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.close()


@router.get(
    "/providers",
    summary="Get list of available social login providers",
)
async def list_providers() -> dict[str, list[dict[str, Any]]]:
    configured_providers = []

    for name in ["google", "github", "discord", "microsoft"]:
        try:
            config = oauth_service.get_provider_config(name)
            is_configured = bool(config.get("client_id") and config.get("client_secret"))
        except Exception:
            is_configured = False

        configured_providers.append({"name": name, "configured": is_configured})

    return {"providers": configured_providers}


@router.post(
    "/{provider}/authorize",
    summary="Get authorization URL and state for social login",
)
async def authorize(
    provider: str,
    body: PKCEAuthorizeRequest,
    redis: Annotated[aioredis.Redis, Depends(get_redis)],
) -> dict[str, str]:
    if provider not in ["google", "github", "discord", "microsoft"]:
        raise OAuthException(
            detail=f"Unsupported provider: '{provider}'",
            code="unsupported_provider",
            status_code=400,
        )

    if body.provider != provider:
        raise OAuthException(
            detail="Provider mismatch between URL and request body.",
            code="provider_error",
            status_code=400,
        )

    url, state = await oauth_service.get_authorization_url(
        provider=provider,
        code_challenge=body.code_challenge,
        code_challenge_method=body.code_challenge_method,
        client_type=body.client_type,
        redis=redis,
    )

    return {"authorization_url": url, "state": state}


@router.get(
    "/{provider}/callback",
    response_model=OAuthLoginResponse,
    summary="OAuth callback redirect landing endpoint",
)
async def callback(
    provider: str,
    code: str,
    state: str,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis: Annotated[aioredis.Redis, Depends(get_redis)],
    x_code_verifier: Annotated[str | None, Header(alias="X-Code-Verifier")] = None,
    code_verifier: Annotated[str | None, Query()] = None,
) -> OAuthLoginResponse:
    verifier = x_code_verifier or code_verifier
    if not verifier:
        raise OAuthException(
            detail="PKCE code verifier parameter is missing.",
            code="pkce_verification_failed",
            status_code=400,
        )

    token_response, client_type = await oauth_service.handle_callback(
        provider=provider,
        code=code,
        state=state,
        code_verifier=verifier,
        db=db,
        redis=redis,
    )

    if client_type == "mobile":
        response.headers["X-Access-Token"] = token_response.access_token
        response.headers["X-Refresh-Token"] = token_response.refresh_token
    else:
        response.set_cookie(
            key="access_token",
            value=token_response.access_token,
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            expires=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            domain=settings.COOKIE_DOMAIN,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
        )
        response.set_cookie(
            key="refresh_token",
            value=token_response.refresh_token,
            httponly=True,
            max_age=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
            expires=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
            domain=settings.COOKIE_DOMAIN,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
        )

    return OAuthLoginResponse(
        user=token_response.user,
        is_new_user=token_response.is_new_user,
        expires_in=token_response.expires_in,
    )


@router.get(
    "/me/accounts",
    response_model=list[ConnectedProvider],
    summary="Get connected social accounts",
)
async def get_me_accounts(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ConnectedProvider]:
    return await oauth_service.get_connected_providers(user_id=current_user.id, db=db)


@router.delete(
    "/accounts/{provider}",
    status_code=status.HTTP_200_OK,
    summary="Unlink a social login account",
)
async def unlink_provider(
    provider: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    await oauth_service.unlink_provider(user_id=current_user.id, provider=provider, db=db)
    return {"message": "Provider unlinked"}
