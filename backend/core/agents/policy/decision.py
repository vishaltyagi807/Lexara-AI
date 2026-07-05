from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class PolicyDecision(BaseModel):
    allowedProviders: list[str] = Field(default_factory=list)
    blockedProviders: list[str] = Field(default_factory=list)
    preferredProviders: list[str] = Field(default_factory=list)
    preferredCapabilities: list[str] = Field(default_factory=list)
    maxBudget: float | None = None
    maxLatency: float | None = None
    allowStreaming: bool = True
    allowCaching: bool = True
    allowReasoning: bool = True
    allowRAG: bool = True
    allowedTools: list[str] = Field(default_factory=list)
    maxTokens: int | None = None
    routingPriority: str = "normal"  # e.g., low, normal, high
    routingHints: dict[str, Any] = Field(default_factory=dict)
    violations: list[str] = Field(default_factory=list)
    reason: str = ""
    confidence: float = 1.0
    policyVersion: int = 0
