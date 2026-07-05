from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from core.conversation.repository import ConversationRepository
from core.conversation.sync import ConversationCache
from core.conversation.mapper import db_message_to_langchain, langchain_to_db_payload
from core.conversation.title_generator import TitleGenerator
from core.conversation.summarizer import ConversationSummarizer
from core.conversation.serializer import to_jsonable

log = logging.getLogger(__name__)

HISTORY_LIMIT = 10  # number of recent messages to load when summary exists
SUMMARY_THRESHOLD = 20  # generate summary when message count exceeds this


class ConversationService:
    def __init__(self) -> None:
        self.repo = ConversationRepository()
        self.cache = ConversationCache()
        self.title_gen = TitleGenerator()
        self.summarizer = ConversationSummarizer()
        self._background_tasks: set[asyncio.Task] = set()

    async def load_conversation_history(
        self,
        db: AsyncSession,
        conversation_id: str | uuid.UUID,
        user_id: str | uuid.UUID | None = None,
    ) -> tuple[list[Any], str | None]:
        """Load conversation history (messages and summary) utilizing cache."""
        conv_str_id = str(conversation_id)
        
        # 1. Try fetching from Redis cache
        cached = await self.cache.get_cached_history(conv_str_id)
        if cached is not None:
            summary = cached.get("summary")
            # Deserialize raw cached messages back to LangChain messages
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            messages = []
            for msg in cached.get("messages", []):
                role = msg.get("role")
                content = msg.get("content")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
                elif role == "system":
                    messages.append(SystemMessage(content=content))
            return messages, summary

        # 2. Cache miss: Load from PostgreSQL
        conv = await self.repo.get_or_create_conversation(db, conversation_id, user_id)
        summary = conv.summary

        # Load recent messages
        db_messages = await self.repo.get_messages(db, conversation_id, limit=HISTORY_LIMIT)
        messages = [db_message_to_langchain(msg) for msg in db_messages]

        # 3. Write back to Redis cache
        cache_messages = [{"role": msg.type, "content": msg.content} for msg in messages]
        await self.cache.set_cached_history(
            conv_str_id,
            {"messages": cache_messages, "summary": summary},
        )

        return messages, summary

    async def save_interaction(
        self,
        db: AsyncSession,
        conversation_id: str | uuid.UUID,
        user_id: str | uuid.UUID | None = None,
        user_content: str = "",
        assistant_content: str = "",
        metadata: dict[str, Any] | None = None,
        title: str | None = None,
    ) -> None:
        """Save a message interaction atomically to DB and invalidate cache."""
        meta = metadata or {}
        
        user_payload = {
            "role": "user",
            "content": user_content,
            "metadata": {},
        }
        
        # Extract assistant response metadata
        assistant_payload = {
            "role": "assistant",
            "content": assistant_content,
            "metadata": {},
            "provider": meta.get("provider"),
            "model": meta.get("model"),
            "prompt_tokens": meta.get("prompt_tokens"),
            "completion_tokens": meta.get("completion_tokens"),
            "total_tokens": meta.get("total_tokens"),
            "latency_ms": meta.get("latency_ms"),
            "finish_reason": meta.get("finish_reason"),
        }

        # Ensure conversation exists and is linked to the user
        conv = await self.repo.get_or_create_conversation(db, conversation_id, user_id)
        if title:
            await self.repo.rename_conversation(db, conversation_id, title)

        # Save to DB atomically
        await self.repo.save_messages_atomic(db, conversation_id, [user_payload, assistant_payload])
        
        # Invalidate Cache
        await self.cache.invalidate_cache(str(conversation_id))

        # Check in background if we should generate title and summary
        import os
        if os.getenv("TESTING") == "1":
            await self._process_post_interaction(conversation_id, user_content)
        else:
            task = asyncio.create_task(self._process_post_interaction(conversation_id, user_content))
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

    async def _process_post_interaction(self, conversation_id: str | uuid.UUID, first_query: str) -> None:
        """Trigger background tasks for title generation and summarization."""
        # Use a fresh database connection session for background processing
        async with AsyncSessionLocal() as db:
            try:
                conv = await self.repo.get_or_create_conversation(db, conversation_id)
                
                # 1. Automatic Title Generation
                if not conv.title:
                    title = await self.title_gen.generate_title(first_query)
                    await self.repo.rename_conversation(db, conversation_id, title)
                    log.info("Background: Generated title '%s' for conversation %s", title, conversation_id)

                # 2. Automatic Summarization Check
                msg_count = await self.repo.count_messages(db, conversation_id)
                if msg_count > SUMMARY_THRESHOLD:
                    # Load all messages to build summary
                    all_messages = await self.repo.get_messages(db, conversation_id, limit=100)
                    # Convert to simple text format
                    messages_text = "\n".join([f"{m.role}: {m.content}" for m in all_messages])
                    
                    new_summary = await self.summarizer.summarize(messages_text, prior_summary=conv.summary)
                    await self.repo.update_summary(db, conversation_id, new_summary)
                    log.info("Background: Summarized conversation %s (Total messages: %d)", conversation_id, msg_count)

                await db.commit()
                # Invalidate cache again to ensure title/summary are synced
                await self.cache.invalidate_cache(str(conversation_id))
            except Exception as exc:
                log.error("Background processing failed for conversation %s: %s", conversation_id, exc)
