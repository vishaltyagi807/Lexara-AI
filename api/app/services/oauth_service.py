from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import redis.asyncio as aioredis
from authlib.integrations.httpx_client import AsyncOAuth2Client
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import OAuthException
from app.models.user import User
from app.schemas.auth import (
    ConnectedProvider,
    OAuthTokenResponse,
    OAuthUserInfo,
    UserResponse,
)
from app.services import pkce_service
from app.services.auth_service import _build_token_response

logger = logging.getLogger(__name__)

PROVIDERS = {
    "google": {
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
        "scopes": ["openid", "email", "profile"],
    },
    "github": {
        "authorize_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "scopes": ["read:user", "user:email"],
    },
    "discord": {
        "authorize_url": "https://discord.com/api/oauth2/authorize",
        "token_url": "https://discord.com/api/oauth2/token",
        "userinfo_url": "https://discord.com/api/users/@me",
        "scopes": ["identify", "email"],
    },
    "microsoft": {
        "authorize_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "userinfo_url": "https://graph.microsoft.com/v1.0/me",
        "scopes": ["openid", "email", "profile", "User.Read"],
    },
}


def get_provider_config(provider: str) -> dict[str, Any]:
    if provider not in PROVIDERS:
        raise OAuthException(
            detail=f"Unsupported OAuth provider: '{provider}'",
            code="unsupported_provider",
            status_code=400,
        )

    config = PROVIDERS[provider].copy()
    if provider == "google":
        config["client_id"] = settings.GOOGLE_CLIENT_ID
        config["client_secret"] = settings.GOOGLE_CLIENT_SECRET
    elif provider == "github":
        config["client_id"] = settings.GITHUB_CLIENT_ID
        config["client_secret"] = settings.GITHUB_CLIENT_SECRET
    elif provider == "discord":
        config["client_id"] = settings.DISCORD_CLIENT_ID
        config["client_secret"] = settings.DISCORD_CLIENT_SECRET
    elif provider == "microsoft":
        config["client_id"] = settings.MICROSOFT_CLIENT_ID
        config["client_secret"] = settings.MICROSOFT_CLIENT_SECRET

    if not config.get("client_id") or not config.get("client_secret"):
        raise OAuthException(
            detail=f"OAuth provider '{provider}' is not configured on the server.",
            code="provider_error",
            status_code=400,
        )

    return config


def _normalize_user_info(provider: str, data: dict[str, Any]) -> OAuthUserInfo:
    provider_id = None
    email = None
    full_name = None
    avatar_url = None

    if provider == "google":
        provider_id = str(data.get("sub", ""))
        email = data.get("email")
        given_name = data.get("given_name", "")
        family_name = data.get("family_name", "")
        full_name = data.get("name") or f"{given_name} {family_name}".strip()
        avatar_url = data.get("picture")

    elif provider == "github":
        provider_id = str(data.get("id", ""))
        email = data.get("email")
        full_name = data.get("name") or data.get("login")
        avatar_url = data.get("avatar_url")

    elif provider == "discord":
        provider_id = str(data.get("id", ""))
        email = data.get("email")
        full_name = data.get("global_name") or data.get("username")
        avatar_hash = data.get("avatar")
        if avatar_hash:
            avatar_url = f"https://cdn.discordapp.com/avatars/{provider_id}/{avatar_hash}.png"

    elif provider == "microsoft":
        provider_id = str(data.get("id", ""))
        email = data.get("mail") or data.get("userPrincipalName")
        full_name = data.get("displayName")
        avatar_url = None

    if not provider_id:
        raise OAuthException(
            detail=f"Could not retrieve unique provider ID from {provider}.",
            code="provider_error",
            status_code=400,
        )

    if not email:
        raise OAuthException(
            detail=f"Could not retrieve email address from {provider} account.",
            code="email_required",
            status_code=400,
        )

    return OAuthUserInfo(
        provider=provider,
        provider_id=provider_id,
        email=email,
        full_name=full_name,
        avatar_url=avatar_url,
    )


async def get_authorization_url(
    provider: str,
    code_challenge: str,
    code_challenge_method: str,
    client_type: str,
    redis: aioredis.Redis,
) -> tuple[str, str]:
    config = get_provider_config(provider)

    if client_type == "web":
        redirect_uri = f"{settings.WEB_OAUTH_REDIRECT_BASE.rstrip('/')}/api/v1/auth/oauth/{provider}/callback"
    elif client_type == "mobile":
        redirect_uri = settings.MOBILE_OAUTH_REDIRECT_URI
    else:
        raise OAuthException(
            detail="Invalid client type specified.",
            code="provider_error",
            status_code=400,
        )

    client = AsyncOAuth2Client(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        scope=" ".join(config["scopes"]),
        redirect_uri=redirect_uri,
    )

    state = pkce_service.generate_state()

    state_data = {
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
        "provider": provider,
        "client_type": client_type,
        "redirect_uri": redirect_uri,
    }

    await redis.setex(
        f"oauth:state:{state}",
        settings.OAUTH_STATE_TTL_SECONDS,
        json.dumps(state_data),
    )

    authorization_url, _ = client.create_authorization_url(
        config["authorize_url"],
        state=state,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
    )

    return authorization_url, state


async def handle_callback(
    provider: str,
    code: str,
    state: str,
    code_verifier: str,
    db: AsyncSession,
    redis: aioredis.Redis,
) -> tuple[OAuthTokenResponse, str]:
    state_key = f"oauth:state:{state}"
    stored_str = await redis.get(state_key)
    if not stored_str:
        raise OAuthException(
            detail="State parameter is invalid or has expired.",
            code="invalid_state",
            status_code=400,
        )

    await redis.delete(state_key)

    stored = json.loads(stored_str)

    if stored.get("provider") != provider:
        raise OAuthException(
            detail="State provider mismatch.",
            code="invalid_state",
            status_code=400,
        )

    try:
        pkce_service.verify_code_challenge(code_verifier, stored["code_challenge"])
    except Exception as exc:
        raise OAuthException(
            detail=f"PKCE verification failed: {exc}",
            code="pkce_verification_failed",
            status_code=400,
        )

    config = get_provider_config(provider)

    client = AsyncOAuth2Client(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        redirect_uri=stored["redirect_uri"],
    )

    try:
        await client.fetch_token(
            config["token_url"],
            code=code,
            code_verifier=code_verifier,
        )
    except Exception as exc:
        logger.error("OAuth token exchange failed for provider %s: %s", provider, exc)
        raise OAuthException(
            detail=f"Failed to exchange authorization code with {provider}.",
            code="provider_error",
            status_code=400,
        )

    try:
        response = await client.get(config["userinfo_url"])
        response.raise_for_status()
        raw_user_info = response.json()

        if provider == "github" and not raw_user_info.get("email"):
            emails_resp = await client.get("https://api.github.com/user/emails")
            if emails_resp.status_code == 200:
                for entry in emails_resp.json():
                    if entry.get("primary") and entry.get("verified"):
                        raw_user_info["email"] = entry.get("email")
                        break
    except Exception as exc:
        logger.error("OAuth profile fetch failed for provider %s: %s", provider, exc)
        raise OAuthException(
            detail=f"Failed to retrieve user profile from {provider}.",
            code="provider_error",
            status_code=400,
        )

    normalized = _normalize_user_info(provider, raw_user_info)

    stmt = select(User).where(
        User.oauth_provider == provider,
        User.oauth_provider_id == normalized.provider_id,
    )
    result = await db.execute(stmt)
    user = result.scalars().first()
    is_new_user = False

    if user:
        if normalized.avatar_url and user.avatar_url != normalized.avatar_url:
            user.avatar_url = normalized.avatar_url
            db.add(user)
            await db.flush()
    else:
        stmt = select(User).where(User.email == normalized.email)
        result = await db.execute(stmt)
        user = result.scalars().first()
        now = datetime.now(tz=timezone.utc)

        if user:
            user.oauth_provider = provider
            user.oauth_provider_id = normalized.provider_id
            user.oauth_connected_at = now
            if normalized.avatar_url:
                user.avatar_url = normalized.avatar_url
            db.add(user)
            await db.flush()
        else:
            is_new_user = True
            user = User(
                email=normalized.email,
                hashed_password=None,
                full_name=normalized.full_name or normalized.email.split("@")[0],
                is_verified=True,
                oauth_provider=provider,
                oauth_provider_id=normalized.provider_id,
                oauth_connected_at=now,
                avatar_url=normalized.avatar_url,
            )
            db.add(user)
            await db.flush()
            await db.refresh(user)

    if not user.is_active:
        raise OAuthException(
            detail="This user account has been deactivated.",
            code="account_locked_out",
            status_code=400,
        )

    std_token = _build_token_response(user)
    response_dto = OAuthTokenResponse(
        access_token=std_token.access_token,
        refresh_token=std_token.refresh_token,
        token_type="bearer",
        expires_in=std_token.expires_in,
        user=UserResponse.model_validate(user),
        is_new_user=is_new_user,
    )

    return response_dto, stored["client_type"]


async def get_connected_providers(user_id: UUID, db: AsyncSession) -> list[ConnectedProvider]:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    providers = []
    if user and user.oauth_provider:
        connected_at = user.oauth_connected_at or user.created_at
        providers.append(
            ConnectedProvider(
                provider=user.oauth_provider,
                connected_at=connected_at,
                avatar_url=user.avatar_url,
            )
        )
    return providers


async def unlink_provider(user_id: UUID, provider: str, db: AsyncSession) -> None:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise OAuthException(
            detail="User not found.",
            code="provider_error",
            status_code=404,
        )

    if user.oauth_provider != provider:
        raise OAuthException(
            detail=f"Provider '{provider}' is not connected to this account.",
            code="provider_error",
            status_code=400,
        )

    if not user.hashed_password:
        raise OAuthException(
            detail="Cannot unlink your only login method. Please set a password first.",
            code="unlink_forbidden",
            status_code=400,
        )

    user.oauth_provider = None
    user.oauth_provider_id = None
    user.oauth_connected_at = None
    db.add(user)
    await db.flush()
