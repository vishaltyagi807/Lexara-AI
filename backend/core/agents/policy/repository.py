from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Integer, String, text, select, update
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base


class RoutingPolicy(Base):
    __tablename__ = "routing_policies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    version: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        index=True,
        nullable=False,
    )

    rules_payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    created_by: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="system",
    )

    description: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
    )

    rollback_from_version: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(tz=timezone.utc),
        server_default=text("now()"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(tz=timezone.utc),
        server_default=text("now()"),
        onupdate=lambda: datetime.now(tz=timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<RoutingPolicy id={self.id} version={self.version} is_active={self.is_active}>"


class PolicyRepository:
    @staticmethod
    async def get_active_policy(db: AsyncSession) -> RoutingPolicy | None:
        """Fetch the currently active routing policy."""
        stmt = select(RoutingPolicy).where(RoutingPolicy.is_active == True).order_by(RoutingPolicy.version.desc())
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_policy_by_version(db: AsyncSession, version: int) -> RoutingPolicy | None:
        """Fetch a specific routing policy by version."""
        stmt = select(RoutingPolicy).where(RoutingPolicy.version == version)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def create_policy(
        db: AsyncSession,
        version: int,
        rules_payload: dict,
        created_by: str = "system",
        description: str | None = None,
        rollback_from_version: int | None = None,
    ) -> RoutingPolicy:
        """Create a new routing policy version."""
        policy = RoutingPolicy(
            version=version,
            rules_payload=rules_payload,
            created_by=created_by,
            description=description,
            rollback_from_version=rollback_from_version,
        )
        db.add(policy)
        await db.flush()
        return policy

    @staticmethod
    async def activate_policy(db: AsyncSession, version: int) -> RoutingPolicy:
        """Activate the policy with the specified version and deactivate all others."""
        # Deactivate all policies
        await db.execute(
            update(RoutingPolicy)
            .where(RoutingPolicy.is_active == True)
            .values(is_active=False)
        )
        
        # Activate target policy
        stmt = (
            update(RoutingPolicy)
            .where(RoutingPolicy.version == version)
            .values(is_active=True, updated_at=datetime.now(tz=timezone.utc))
            .returning(RoutingPolicy)
        )
        res = await db.execute(stmt)
        policy = res.scalar_one_or_none()
        if not policy:
            raise ValueError(f"Policy with version {version} not found.")
        return policy

    @staticmethod
    async def get_policy_history(db: AsyncSession, limit: int = 50) -> list[RoutingPolicy]:
        """Fetch list of policy versions, sorted by version descending."""
        stmt = select(RoutingPolicy).order_by(RoutingPolicy.version.desc()).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())
