from __future__ import annotations

import asyncio
import os
import unittest
import uuid

os.environ["TESTING"] = "1"

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from core.conversation.service import ConversationService
from core.conversation.repository import ConversationRepository
from core.conversation.sync import ConversationCache


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


class TestConversationService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine, self.SessionLocal = _make_session_factory()
        self.service = ConversationService()
        self.cache = ConversationCache()
        self.repo = ConversationRepository()

        # Unique ID for testing
        self.conversation_id = uuid.uuid4()

        # Clear cache before starting
        await self.cache.invalidate_cache(str(self.conversation_id))

    async def asyncTearDown(self):
        if self.service._background_tasks:
            await asyncio.gather(
                *list(self.service._background_tasks), return_exceptions=True
            )
        await self.cache.invalidate_cache(str(self.conversation_id))
        await self.engine.dispose()

    async def test_load_and_save_interaction(self):
        async with self.SessionLocal() as db:
            # 1. Load history of a new conversation (empty history + None summary)
            history, summary = await self.service.load_conversation_history(
                db, self.conversation_id
            )
            self.assertEqual(len(history), 0)
            self.assertIsNone(summary)

            # 2. Save an interaction
            metadata = {
                "provider": "openai",
                "model": "gpt-4o",
                "prompt_tokens": 10,
                "completion_tokens": 15,
                "total_tokens": 25,
                "latency_ms": 100,
                "finish_reason": "stop",
            }
            await self.service.save_interaction(
                db,
                self.conversation_id,
                user_content="Hello, AI!",
                assistant_content="Hello, human! How can I help you?",
                metadata=metadata,
            )
            await db.commit()

        # 3. Reload history (should have 2 messages: user first, then assistant)
        async with self.SessionLocal() as db:
            history2, summary2 = await self.service.load_conversation_history(
                db, self.conversation_id
            )
            self.assertEqual(len(history2), 2)
            self.assertEqual(history2[0].content, "Hello, AI!")
            self.assertEqual(history2[1].content, "Hello, human! How can I help you?")

            # Background title generation runs synchronously in TESTING mode
            conv = await self.repo.get_or_create_conversation(
                db, self.conversation_id
            )
            self.assertIsNotNone(conv.title)
            self.assertGreater(len(conv.title), 0)
