from __future__ import annotations
import sys
import os

# Adds backend/ to path so `import core` resolves to backend/core/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import logging
from contextlib import asynccontextmanager
# ... rest unchanged

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.exceptions import register_exception_handlers

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting %s …", settings.APP_NAME)
    from app.db.session import engine
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        logger.info("Database connection verified ✓")
    except Exception as exc:
        logger.error("Database connection FAILED: %s", exc)

    try:
        import redis.asyncio as aioredis
        r: aioredis.Redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        async with r:
            await r.ping()
        logger.info("Redis connection verified ✓")
    except Exception as exc:
        logger.warning("Redis connection FAILED: %s — token blacklisting will not work.", exc)

    # Initialize Policy Cache and Subscriber
    from core.agents.policy.cache import PolicyCache
    from core.agents.policy.repository import PolicyRepository
    from core.agents.policy.subscriber import start_policy_subscriber
    from app.db.session import AsyncSessionLocal
    import asyncio

    # Load initial active policy from DB
    try:
        async with AsyncSessionLocal() as db:
            active_policy = await PolicyRepository.get_active_policy(db)
            if active_policy:
                PolicyCache().set_policy(active_policy.version, active_policy.rules_payload)
                logger.info("Loaded active policy version %d on startup.", active_policy.version)
            else:
                # Seed a default policy if none exists
                default_rules = {
                    "provider": {
                        "allowed_providers": ["openai", "groq", "anthropic"],
                        "blocked_providers": [],
                        "preferred_providers": ["groq"]
                    },
                    "budget": {
                        "max_budget_per_request": 0.05
                    },
                    "latency": {
                        "max_latency_ms": 5000
                    },
                    "availability": {
                        "min_uptime_pct": 99.0
                    },
                    "reasoning": {
                        "allow_reasoning": True
                    },
                    "tools": {
                        "allowed_tools": ["calculator", "web_search"]
                    },
                    "rag": {
                        "allow_rag": True
                    },
                    "tenant": {
                        "allowed_tenants": [],
                        "blocked_ips": []
                    },
                    "security": {
                        "block_prompt_injection": True
                    }
                }
                await PolicyRepository.create_policy(
                    db,
                    version=1,
                    rules_payload=default_rules,
                    created_by="system",
                    description="Default seeded system policy"
                )
                await PolicyRepository.activate_policy(db, version=1)
                await db.commit()
                PolicyCache().set_policy(1, default_rules)
                logger.info("No policy found. Seeded and loaded default version 1.")
    except Exception as exc:
        logger.error("Failed to initialize PolicyCache from DB: %s", exc)

    # Start policy subscriber
    subscriber_task = asyncio.create_task(start_policy_subscriber())

    yield

    # Cancel Redis subscriber
    try:
        subscriber_task.cancel()
        await subscriber_task
    except asyncio.CancelledError:
        pass
    except Exception as exc:
        logger.warning("Error cancelling policy subscriber: %s", exc)

    logger.info("Shutting down %s …", settings.APP_NAME)
    from app.db.session import engine
    await engine.dispose()
    logger.info("Database engine disposed ✓")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Authentication and API gateway for the Lexara-AI platform.",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from starlette.middleware.sessions import SessionMiddleware
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="oauth_session",
        same_site="lax",
        https_only=settings.COOKIE_SECURE,
    )

    register_exception_handlers(app)

    from app.api.v1.auth.basic import router as auth_router
    app.include_router(auth_router)

    from app.api.v1.auth.oauth import router as oauth_router
    app.include_router(oauth_router)

    # ── Chat router (AI layer) ─────────────────────────────────────────────
    from app.api.v1.chat.chat import router as chat_router
    app.include_router(chat_router, prefix="/api/v1")
    # ──────────────────────────────────────────────────────────────────────

    try:
        from prometheus_fastapi_instrumentator import Instrumentator
        Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
        logger.info("Prometheus metrics initialized ✓")
    except ImportError:
        logger.info("prometheus-fastapi-instrumentator not installed — skipping metrics.")

    return app


app = create_app()