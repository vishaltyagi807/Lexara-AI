from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field

from core.agents.policy.schemas import EvaluationContext


class PartialPolicyDecision(BaseModel):
    allowedProviders: list[str] | None = None
    blockedProviders: list[str] | None = None
    preferredProviders: list[str] | None = None
    preferredCapabilities: list[str] | None = None
    maxBudget: float | None = None
    maxLatency: float | None = None
    allowStreaming: bool | None = None
    allowCaching: bool | None = None
    allowReasoning: bool | None = None
    allowRAG: bool | None = None
    allowedTools: list[str] | None = None
    maxTokens: int | None = None
    routingPriority: str | None = None
    routingHints: dict[str, Any] | None = None
    violations: list[str] = Field(default_factory=list)
    reason: str | None = None
    confidence: float | None = None


class PolicyRule(ABC):
    @abstractmethod
    def evaluate(self, context: EvaluationContext, rules_config: dict[str, Any]) -> PartialPolicyDecision:
        """Evaluate a specific policy constraint against the request context.

        Args:
            context: The EvaluationContext representing the request/client context.
            rules_config: The rules payload dictionary from the active routing policy.

        Returns:
            A PartialPolicyDecision containing the constraints of this rule.
        """
        pass
