from __future__ import annotations

import asyncio
import os
import unittest
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from core.agents.policy.cache import PolicyCache
from core.agents.policy.repository import PolicyRepository
from core.agents.policy.subscriber import start_policy_subscriber, REDIS_CHANNEL


class TestRedisSync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.cache = PolicyCache()
        self.cache.clear()
        
        # Start subscriber background task
        self.subscriber_task = asyncio.create_task(start_policy_subscriber())
        # Yield to let subscriber start
        await asyncio.sleep(0.5)

    async def asyncTearDown(self):
        self.subscriber_task.cancel()
        try:
            await self.subscriber_task
        except asyncio.CancelledError:
            pass

    async def test_redis_pubsub_sync(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # 1. Create a new policy version in PostgreSQL
        test_rules = {"provider": {"allowed_providers": ["groq", "anthropic"]}}
        
        async with AsyncSessionLocal() as db:
            # Seed policy version 100
            policy = await PolicyRepository.create_policy(
                db,
                version=100,
                rules_payload=test_rules,
                created_by="test-suite",
                description="Test pubsub synchronization",
            )
            await PolicyRepository.activate_policy(db, version=100)
            await db.commit()

        # Verify cache does not have version 100 yet
        self.assertNotEqual(self.cache.current_version(), 100)

        # 2. Publish updated signal to Redis
        client = aioredis.from_url(redis_url, decode_responses=True)
        async with client:
            await client.publish(REDIS_CHANNEL, "version=100")

        # 3. Wait for subscriber task to pick it up and reload cache
        for _ in range(20):
            await asyncio.sleep(0.2)
            if self.cache.current_version() == 100:
                break

        # Verify cache is successfully updated
        self.assertEqual(self.cache.current_version(), 100)
        self.assertEqual(self.cache.get_active_policy(), test_rules)
