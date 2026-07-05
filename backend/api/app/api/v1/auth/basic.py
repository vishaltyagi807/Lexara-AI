from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Annotated
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ConnectedAccount,
    LoginRequest,
    RefreshResponse,
    RegisterRequest,
    TokenResponse,
    UpdateMeRequest,
    UserResponse,
)
from app.services import auth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

_bearer_scheme = HTTPBearer(auto_error=False)


async def _get_raw_token(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ] = None,
) -> str:
    token = request.headers.get("X-Access-Token")
    if not token:
        token = request.cookies.get("access_token")
    if not token and credentials and credentials.credentials:
        token = credentials.credentials

    if not token:
        from app.core.exceptions import AuthException
        raise AuthException(
            detail="Authentication token missing or malformed.",
            code="MISSING_TOKEN",
        )

    payload = decode_token(token)
    if payload.get("token_type") != "access":
        from app.core.exceptions import AuthException
        raise AuthException(
            detail="Invalid token type. Only access tokens are allowed.",
            code="INVALID_TOKEN_TYPE",
        )
    return token




@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    data: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    user = await auth_service.register_user(db=db, data=data)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Log in with email and password",
)
async def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    user, token_response = await auth_service.login_user(db=db, email=data.email, password=data.password)

    client_type = request.headers.get("X-Client-Type", "web").lower()
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
    return UserResponse.model_validate(user)




@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh an access token",
)
async def refresh(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RefreshResponse:
    refresh_token = request.headers.get("X-Refresh-Token") or request.cookies.get("refresh_token")
    if not refresh_token:
        from app.core.exceptions import AuthException
        raise AuthException(
            detail="Refresh token missing from cookie or header.",
            code="MISSING_REFRESH_TOKEN",
        )
    token_response = await auth_service.refresh_tokens(db=db, refresh_token=refresh_token)

    client_type = request.headers.get("X-Client-Type", "web").lower()
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
    return RefreshResponse(expires_in=settings.ACCESS_TOKEN_EXPIRE_SECONDS)




async def authenticate_logout(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ] = None,
) -> tuple[User, list[str]]:
    from sqlalchemy import select
    from app.core.exceptions import AuthException, ForbiddenException
    from app.services.auth_service import get_current_user as svc_get_current_user

    tokens_to_blacklist = []
    user = None
    last_error = None

    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    bearer_token = credentials.credentials if (credentials and credentials.credentials) else None

    if access_token:
        try:
            payload = decode_token(access_token)
            if payload.get("token_type") == "access":
                tokens_to_blacklist.append(access_token)
                if not user:
                    user = await svc_get_current_user(db=db, token=access_token)
        except Exception as e:
            last_error = e

    if refresh_token:
        try:
            payload = decode_token(refresh_token)
            if payload.get("token_type") == "refresh":
                tokens_to_blacklist.append(refresh_token)
                if not user:
                    user_id = payload.get("sub")
                    if user_id:
                        stmt = select(User).where(User.id == user_id)
                        result = await db.execute(stmt)
                        user = result.scalars().first()
        except Exception as e:
            last_error = e

    if bearer_token:
        try:
            payload = decode_token(bearer_token)
            t_type = payload.get("token_type")
            if t_type in ("access", "refresh"):
                tokens_to_blacklist.append(bearer_token)
                if not user:
                    user_id = payload.get("sub")
                    if user_id:
                        stmt = select(User).where(User.id == user_id)
                        result = await db.execute(stmt)
                        user = result.scalars().first()
        except Exception as e:
            last_error = e

    if user:
        if not user.is_active:
            raise ForbiddenException(
                detail="This account has been deactivated.",
                code="ACCOUNT_INACTIVE",
            )
        return user, list(set(tokens_to_blacklist))

    if last_error:
        raise last_error
    raise AuthException(
        detail="Authentication token missing or invalid.",
        code="MISSING_TOKEN",
    )




@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Log out (blacklist current token)",
)
async def logout(
    logout_data: Annotated[tuple[User, list[str]], Depends(authenticate_logout)],
    response: Response,
) -> dict[str, str]:
    current_user, tokens_to_blacklist = logout_data

    redis_client: aioredis.Redis = aioredis.from_url(
        settings.REDIS_URL, decode_responses=True
    )
    async with redis_client:
        for token in tokens_to_blacklist:
            try:
                payload = decode_token(token)
                exp_timestamp = payload.get("exp", 0)
                now_timestamp = int(datetime.now(tz=timezone.utc).timestamp())
                ttl = max(exp_timestamp - now_timestamp, 1)
                await redis_client.setex(f"blacklist:{token}", ttl, "1")
            except Exception:
                pass

    response.delete_cookie(
        key="access_token",
        domain=settings.COOKIE_DOMAIN,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    response.delete_cookie(
        key="refresh_token",
        domain=settings.COOKIE_DOMAIN,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )

    logger.info("Blacklisted %d tokens for user %s on logout.", len(tokens_to_blacklist), current_user.id)
    return {"message": "Logged out successfully."}




@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:

    return UserResponse.model_validate(current_user)




@router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
)
async def update_me(
    data: UpdateMeRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    if data.full_name is not None:
        current_user.full_name = data.full_name
        current_user.updated_at = datetime.now(tz=timezone.utc)
        db.add(current_user)
        await db.flush()
        await db.refresh(current_user)

    return UserResponse.model_validate(current_user)




@router.get(
    "/me/accounts",
    response_model=list[ConnectedAccount],
    status_code=status.HTTP_200_OK,
    summary="Get connected social accounts",
)
async def get_me_accounts(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list[ConnectedAccount]:
    accounts = []
    if current_user.oauth_provider:
        connected_at = current_user.oauth_connected_at or current_user.created_at
        accounts.append(
            ConnectedAccount(
                provider=current_user.oauth_provider,
                connected_at=connected_at,
            )
        )
    return accounts
