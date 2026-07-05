from __future__ import annotations

from typing import Any
from core.agents.policy.rules import PolicyRule, PartialPolicyDecision
from core.agents.policy.schemas import EvaluationContext


class ToolsRule(PolicyRule):
    def evaluate(self, context: EvaluationContext, rules_config: dict[str, Any]) -> PartialPolicyDecision:
        config = rules_config.get("tools", {})
        allowed_tools = config.get("allowed_tools")

        violations = []
        requested_tools = context.metadata.get("requested_tools", [])
        if allowed_tools is not None:
            for tool in requested_tools:
                if tool not in allowed_tools:
                    violations.append(f"Tool '{tool}' is not allowed by policy.")

        return PartialPolicyDecision(
            allowedTools=allowed_tools,
            violations=violations,
            reason="Tool calling policy evaluated." if violations else None,
        )
