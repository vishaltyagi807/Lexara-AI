from __future__ import annotations

from typing import Any
from core.agents.policy.rules import PolicyRule, PartialPolicyDecision
from core.agents.policy.schemas import EvaluationContext


class ReasoningRule(PolicyRule):
    def evaluate(self, context: EvaluationContext, rules_config: dict[str, Any]) -> PartialPolicyDecision:
        config = rules_config.get("reasoning", {})
        allow_reasoning = config.get("allow_reasoning", True)
        require_reasoning_for_complexity = config.get("require_reasoning_for_complexity_above", 7)

        violations = []
        if not allow_reasoning and "reasoning" in context.required_capabilities:
            violations.append("Reasoning capability is disabled by policy.")

        # Check if we should enforce reasoning based on query complexity score (passed in metadata/context)
        complexity = context.metadata.get("complexity_score", 0)
        force_reasoning = False
        if allow_reasoning and complexity > require_reasoning_for_complexity:
            force_reasoning = True

        hints = {}
        if force_reasoning:
            hints["force_reasoning"] = True

        return PartialPolicyDecision(
            allowReasoning=allow_reasoning,
            routingHints=hints if hints else None,
            violations=violations,
            reason="Reasoning capability policy evaluated." if violations else None,
        )
