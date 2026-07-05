from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select, update, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.conversation.models import Conversation, Message
from app.models.user import User

log = logging.getLogger(__name__)


class ConversationRepository:
    @staticmethod
    async def get_or_create_conversation(
        db: AsyncSession,
        conversation_id: str | uuid.UUID,
        user_id: str | uuid.UUID | None = None,
    ) -> Conversation:
        """Fetch a conversation by ID, or create it if not found."""
        if isinstance(conversation_id, str):
            try:
                conv_uuid = uuid.UUID(conversation_id)
            except ValueError:
                conv_uuid = uuid.uuid4()
        else:
            conv_uuid = conversation_id

        user_uuid = None
        if user_id:
            if isinstance(user_id, str):
                try:
                    user_uuid = uuid.UUID(user_id)
                except ValueError:
                    user_uuid = None
            else:
                user_uuid = user_id
            
            if user_uuid:
                user_stmt = select(User).where(User.id == user_uuid)
                user_res = await db.execute(user_stmt)
                if user_res.scalar_one_or_none() is None:
                    user_uuid = None

        stmt = select(Conversation).where(Conversation.id == conv_uuid)
        res = await db.execute(stmt)
        conv = res.scalar_one_or_none()

        if conv is None:
            log.info("ConversationRepository: Creating conversation %s", conv_uuid)
            conv = Conversation(
                id=conv_uuid,
                user_id=user_uuid,
                title=None,
                summary=None,
                is_archived=False,
                is_pinned=False,
                is_deleted=False,
            )
            db.add(conv)
            await db.flush()
        return conv

    @staticmethod
    async def get_messages(
        db: AsyncSession,
        conversation_id: str | uuid.UUID,
        limit: int = 20,
    ) -> list[Message]:
        """Fetch the most recent messages for a conversation, in chronological order."""
        if isinstance(conversation_id, str):
            conv_uuid = uuid.UUID(conversation_id)
        else:
            conv_uuid = conversation_id

        stmt = (
            select(Message)
            .where(Message.conversation_id == conv_uuid)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        messages = list(res.scalars().all())
        # Reverse to return in chronological order
        messages.reverse()
        return messages

    @staticmethod
    async def count_messages(db: AsyncSession, conversation_id: str | uuid.UUID) -> int:
        """Count total messages in a conversation."""
        if isinstance(conversation_id, str):
            conv_uuid = uuid.UUID(conversation_id)
        else:
            conv_uuid = conversation_id

        stmt = select(Message).where(Message.conversation_id == conv_uuid)
        res = await db.execute(stmt)
        return len(res.scalars().all())

    @staticmethod
    async def save_messages_atomic(
        db: AsyncSession,
        conversation_id: str | uuid.UUID,
        messages_data: list[dict[str, Any]],
    ) -> list[Message]:
        """Atomically save multiple messages to a conversation in a single transaction."""
        if isinstance(conversation_id, str):
            conv_uuid = uuid.UUID(conversation_id)
        else:
            conv_uuid = conversation_id

        saved_messages = []
        try:
            import datetime as dt
            base_now = datetime.now(tz=timezone.utc)
            for idx, item in enumerate(messages_data):
                msg = Message(
                    id=uuid.uuid4(),
                    conversation_id=conv_uuid,
                    role=item["role"],
                    content=item["content"],
                    tool_calls=item.get("tool_calls"),
                    tool_outputs=item.get("tool_outputs"),
                    attachments=item.get("attachments"),
                    metadata_payload=item.get("metadata", {}),
                    provider=item.get("provider"),
                    model=item.get("model"),
                    prompt_tokens=item.get("prompt_tokens"),
                    completion_tokens=item.get("completion_tokens"),
                    total_tokens=item.get("total_tokens"),
                    latency_ms=item.get("latency_ms"),
                    finish_reason=item.get("finish_reason"),
                    created_at=base_now + dt.timedelta(microseconds=idx * 10),
                )
                db.add(msg)
                saved_messages.append(msg)
            
            # Update updated_at of the conversation
            await db.execute(
                update(Conversation)
                .where(Conversation.id == conv_uuid)
                .values(updated_at=datetime.now(tz=timezone.utc))
            )
            await db.flush()
            return saved_messages
        except Exception as exc:
            log.error("ConversationRepository: Failed to save messages atomically: %s", exc)
            raise

    @staticmethod
    async def update_summary(db: AsyncSession, conversation_id: str | uuid.UUID, summary: str) -> None:
        """Update the conversation summary."""
        if isinstance(conversation_id, str):
            conv_uuid = uuid.UUID(conversation_id)
        else:
            conv_uuid = conversation_id

        await db.execute(
            update(Conversation)
            .where(Conversation.id == conv_uuid)
            .values(summary=summary, updated_at=datetime.now(tz=timezone.utc))
        )
        await db.flush()

    @staticmethod
    async def rename_conversation(db: AsyncSession, conversation_id: str | uuid.UUID, title: str) -> None:
        """Rename a conversation."""
        if isinstance(conversation_id, str):
            conv_uuid = uuid.UUID(conversation_id)
        else:
            conv_uuid = conversation_id

        await db.execute(
            update(Conversation)
            .where(Conversation.id == conv_uuid)
            .values(title=title, updated_at=datetime.now(tz=timezone.utc))
        )
        await db.flush()

    @staticmethod
    async def archive_conversation(db: AsyncSession, conversation_id: str | uuid.UUID, is_archived: bool = True) -> None:
        """Archive or unarchive a conversation."""
        if isinstance(conversation_id, str):
            conv_uuid = uuid.UUID(conversation_id)
        else:
            conv_uuid = conversation_id

        await db.execute(
            update(Conversation)
            .where(Conversation.id == conv_uuid)
            .values(is_archived=is_archived, updated_at=datetime.now(tz=timezone.utc))
        )
        await db.flush()

    @staticmethod
    async def soft_delete_conversation(db: AsyncSession, conversation_id: str | uuid.UUID, is_deleted: bool = True) -> None:
        """Soft delete or restore a conversation."""
        if isinstance(conversation_id, str):
            conv_uuid = uuid.UUID(conversation_id)
        else:
            conv_uuid = conversation_id

        await db.execute(
            update(Conversation)
            .where(Conversation.id == conv_uuid)
            .values(is_deleted=is_deleted, updated_at=datetime.now(tz=timezone.utc))
        )
        await db.flush()

    @staticmethod
    async def get_user_conversations(
        db: AsyncSession,
        user_id: str | uuid.UUID,
        limit: int = 50,
        offset: int = 0,
        search: str | None = None,
        include_archived: bool = False,
    ) -> list[Conversation]:
        """Fetch list of user conversations with search and pagination filters."""
        if isinstance(user_id, str):
            user_uuid = uuid.UUID(user_id)
        else:
            user_uuid = user_id

        conditions = [
            Conversation.user_id == user_uuid,
            Conversation.is_deleted == False,
        ]
        if not include_archived:
            conditions.append(Conversation.is_archived == False)
        
        if search:
            conditions.append(Conversation.title.ilike(f"%{search}%"))

        stmt = (
            select(Conversation)
            .where(and_(*conditions))
            .order_by(Conversation.is_pinned.desc(), Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())
