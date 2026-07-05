from __future__ import annotations

import json
import logging
import os
from typing import Any
import redis.asyncio as aioredis

log = logging.getLogger(__name__)

CACHE_TTL = 1800  # 30 minutes


class ConversationCache:
    def __init__(self) -> None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = aioredis.from_url(redis_url, decode_responses=True)

    def _get_key(self, conversation_id: str) -> str:
        return f"conversation:{conversation_id}"

    async def get_cached_history(self, conversation_id: str) -> dict[str, Any] | None:
        """Fetch cached conversation messages and summary from Redis."""
        key = self._get_key(conversation_id)
        try:
            data = await self.redis_client.get(key)
            if data:
                log.info("ConversationCache: Cache hit for %s", conversation_id)
                return json.loads(data)
        except Exception as exc:
            log.warning("ConversationCache: Failed to read from cache: %s", exc)
        return None

    async def set_cached_history(self, conversation_id: str, payload: dict[str, Any]) -> None:
        """Cache conversation history (messages and summary) in Redis."""
        key = self._get_key(conversation_id)
        try:
            await self.redis_client.set(key, json.dumps(payload), ex=CACHE_TTL)
            log.info("ConversationCache: Cache write successful for %s", conversation_id)
        except Exception as exc:
            log.warning("ConversationCache: Failed to write to cache: %s", exc)

    async def invalidate_cache(self, conversation_id: str) -> None:
        """Invalidate the cache for the updated conversation."""
        key = self._get_key(conversation_id)
        try:
            await self.redis_client.delete(key)
            log.info("ConversationCache: Cache invalidated for %s", conversation_id)
        except Exception as exc:
            log.warning("ConversationCache: Failed to delete cache: %s", exc)
