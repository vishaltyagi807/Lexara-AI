from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthException, ConflictException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse

logger = logging.getLogger(__name__)


async def _publish_user_event(event_type: str, payload: dict) -> None:
    if not settings.KAFKA_BOOTSTRAP_SERVERS:
        logger.info(
            "Kafka not configured — event %s logged locally: %s",
            event_type,
            json.dumps(payload, default=str),
        )
        return

    try:
        from aiokafka import AIOKafkaProducer

        producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        )
        await producer.start()
        try:
            message = {"event": event_type, "data": payload, "timestamp": datetime.now(tz=timezone.utc).isoformat()}
            await producer.send_and_wait(settings.KAFKA_USER_EVENTS_TOPIC, value=message)
            logger.info("Published %s to Kafka topic '%s'.", event_type, settings.KAFKA_USER_EVENTS_TOPIC)
        finally:
            await producer.stop()
    except Exception:
        logger.exception("Failed to publish Kafka event %s — continuing without blocking.", event_type)




def _build_token_response(user: User) -> TokenResponse:
    subject = str(user.id)
    access = create_access_token(data={"sub": subject, "email": user.email})
    refresh = create_refresh_token(data={"sub": subject})
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
    )




async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    existing = result.scalars().first()
    if existing is not None:
        raise ConflictException(
            detail=f"A user with email '{data.email}' already exists.",
            code="EMAIL_TAKEN",
        )

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    await _publish_user_event(
        "user.registered",
        {"user_id": str(user.id), "email": user.email},
    )

    return user


async def login_user(db: AsyncSession, email: str, password: str) -> tuple[User, TokenResponse]:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user is None or not verify_password(password, user.hashed_password):
        raise AuthException(
            detail="Invalid email or password.",
            code="INVALID_CREDENTIALS",
        )

    if not user.is_active:
        raise AuthException(
            detail="This account has been deactivated.",
            code="ACCOUNT_INACTIVE",
        )

    return user, _build_token_response(user)


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> TokenResponse:
    payload = decode_token(refresh_token)

    if payload.get("token_type") != "refresh":
        raise AuthException(detail="Invalid token type.", code="INVALID_TOKEN_TYPE")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthException(detail="Token missing subject.", code="INVALID_TOKEN")

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise AuthException(detail="User not found.", code="USER_NOT_FOUND")

    if not user.is_active:
        raise AuthException(detail="Account is deactivated.", code="ACCOUNT_INACTIVE")

    return _build_token_response(user)


async def get_current_user(db: AsyncSession, token: str) -> User:
    payload = decode_token(token)

    if payload.get("token_type") != "access":
        raise AuthException(
            detail="Invalid token type. Only access tokens are allowed.",
            code="INVALID_TOKEN_TYPE",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise AuthException(detail="Token missing subject.", code="INVALID_TOKEN")

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise AuthException(detail="User not found.", code="USER_NOT_FOUND")

    return user
