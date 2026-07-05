from __future__ import annotations

import asyncio
import os
import unittest
import redis.asyncio as aioredis

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from core.agents.policy.cache import PolicyCache
from core.agents.policy.repository import PolicyRepository
from core.agents.policy.subscriber import start_policy_subscriber, REDIS_CHANNEL


def _make_session_factory():
    """Create a fresh engine + session factory bound to the current event loop."""
    from app.core.config import settings
    eng = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=2,
        max_overflow=2,
    )
    factory = async_sessionmaker(
        bind=eng,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    return eng, factory


class TestRedisSync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine, self.SessionLocal = _make_session_factory()
        self.cache = PolicyCache()
        self.cache.clear()

        # Start subscriber with a fresh session factory bound to this event loop
        self.subscriber_task = asyncio.create_task(
            start_policy_subscriber(session_factory=self.SessionLocal)
        )
        # Yield to let subscriber start
        await asyncio.sleep(0.5)

    async def asyncTearDown(self):
        self.subscriber_task.cancel()
        try:
            await self.subscriber_task
        except asyncio.CancelledError:
            pass
        await self.engine.dispose()

    async def test_redis_pubsub_sync(self):
        import random
        version = random.randint(1000, 999999)
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

        # 1. Create a new policy version in PostgreSQL
        test_rules = {"provider": {"allowed_providers": ["groq", "anthropic"]}}

        async with self.SessionLocal() as db:
            await PolicyRepository.create_policy(
                db,
                version=version,
                rules_payload=test_rules,
                created_by="test-suite",
                description="Test pubsub synchronization",
            )
            await PolicyRepository.activate_policy(db, version=version)
            await db.commit()

        # Verify cache does not have version yet
        self.assertNotEqual(self.cache.current_version(), version)

        # 2. Publish updated signal to Redis
        client = aioredis.from_url(redis_url, decode_responses=True)
        async with client:
            await client.publish(REDIS_CHANNEL, f"version={version}")

        # 3. Wait for subscriber task to pick it up and reload cache
        for _ in range(20):
            await asyncio.sleep(0.2)
            if self.cache.current_version() == version:
                break

        # Verify cache is successfully updated
        self.assertEqual(self.cache.current_version(), version)
        self.assertEqual(self.cache.get_active_policy(), test_rules)
