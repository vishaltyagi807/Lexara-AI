from __future__ import annotations

from typing import Any
from core.agents.policy.rules import PolicyRule, PartialPolicyDecision
from core.agents.policy.schemas import EvaluationContext


class LatencyRule(PolicyRule):
    def evaluate(self, context: EvaluationContext, rules_config: dict[str, Any]) -> PartialPolicyDecision:
        config = rules_config.get("latency", {})
        max_latency = config.get("max_latency_ms")

        violations = []
        if max_latency is not None and context.current_latency_ms is not None:
            if context.current_latency_ms > max_latency:
                violations.append(
                    f"Current latency ({context.current_latency_ms}ms) exceeds maximum latency constraint ({max_latency}ms)."
                )

        return PartialPolicyDecision(
            maxLatency=max_latency,
            violations=violations,
            reason="Latency limits checked." if violations else None,
        )
