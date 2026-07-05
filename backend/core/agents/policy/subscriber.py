from __future__ import annotations

import asyncio
import json
import logging
import os
import redis.asyncio as aioredis

from app.db.session import AsyncSessionLocal
from core.agents.policy.cache import PolicyCache
from core.agents.policy.repository import PolicyRepository

log = logging.getLogger(__name__)

REDIS_CHANNEL = "policy.updated"


async def reload_active_policy(session_factory=None) -> None:
    """Fetch the active policy from database and reload the cache."""
    if session_factory is None:
        session_factory = AsyncSessionLocal
    try:
        async with session_factory() as db:
            active_policy = await PolicyRepository.get_active_policy(db)
            if active_policy:
                PolicyCache().set_policy(
                    version=active_policy.version,
                    rules_payload=active_policy.rules_payload,
                )
                log.info(
                    "reload_active_policy: Reloaded active policy version %d successfully.",
                    active_policy.version,
                )
            else:
                log.warning("reload_active_policy: No active policy found in database.")
    except Exception as exc:
        log.error("reload_active_policy: Failed to load policy from database: %s", exc)


async def start_policy_subscriber(session_factory=None) -> None:
    """Redis Pub/Sub subscriber task.

    Listens to 'policy.updated' channel. When a notification is received,
    reloads the latest active policy from PostgreSQL.
    """
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    log.info("start_policy_subscriber: Connecting to Redis at %s", redis_url)
    
    while True:
        try:
            client = aioredis.from_url(redis_url, decode_responses=True)
            async with client.pubsub() as pubsub:
                await pubsub.subscribe(REDIS_CHANNEL)
                log.info("start_policy_subscriber: Subscribed to channel '%s' successfully.", REDIS_CHANNEL)
                
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        data = message["data"]
                        log.info("start_policy_subscriber: Received policy update event. Data: %s", data)
                        
                        # Process update
                        try:
                            await reload_active_policy(session_factory=session_factory)
                        except Exception as e:
                            log.error("start_policy_subscriber: Error reloading policy: %s", e)
                            
        except asyncio.CancelledError:
            log.info("start_policy_subscriber: Cancelled.")
            break
        except Exception as exc:
            log.error("start_policy_subscriber: Connection failed, retrying in 5 seconds... Error: %s", exc)
            await asyncio.sleep(5)
