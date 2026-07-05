from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class EvaluationContext(BaseModel):
    query: str
    user_id: str | None = None
    tenant_id: str | None = None
    current_budget_spent: float | None = None
    current_latency_ms: float | None = None
    required_capabilities: list[str] = Field(default_factory=list)
    provider: str | None = None
    client_ip: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PolicyCreateRequest(BaseModel):
    version: int
    rules_payload: dict[str, Any]
    created_by: str = "system"
    description: str | None = None
    rollback_from_version: int | None = None


class PolicyResponse(BaseModel):
    id: str
    version: int
    rules_payload: dict[str, Any]
    is_active: bool
    created_by: str
    description: str | None
    rollback_from_version: int | None
    created_at: str
    updated_at: str
