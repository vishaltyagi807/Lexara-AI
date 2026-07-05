from __future__ import annotations

from typing import Any
from core.agents.policy.rules import PolicyRule, PartialPolicyDecision
from core.agents.policy.schemas import EvaluationContext


class AvailabilityRule(PolicyRule):
    def evaluate(self, context: EvaluationContext, rules_config: dict[str, Any]) -> PartialPolicyDecision:
        config = rules_config.get("availability", {})
        min_uptime = config.get("min_uptime_pct", 99.0)
        fallback_enabled = config.get("fallback_enabled", True)

        hints = {
            "min_uptime_pct": min_uptime,
            "fallback_enabled": fallback_enabled,
        }

        return PartialPolicyDecision(
            routingHints=hints,
            violations=[],
            reason="Availability checks initialized."
        )
