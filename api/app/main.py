from __future__ import annotations
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



    yield

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

    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
        logger.info("Prometheus metrics initialized ✓")
    except ImportError:
        logger.info("prometheus-fastapi-instrumentator not installed — skipping metrics.")

    return app

app = create_app()
