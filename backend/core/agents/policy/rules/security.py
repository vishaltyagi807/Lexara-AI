from __future__ import annotations

from typing import Any
import re
from core.agents.policy.rules import PolicyRule, PartialPolicyDecision
from core.agents.policy.schemas import EvaluationContext


class SecurityRule(PolicyRule):
    def evaluate(self, context: EvaluationContext, rules_config: dict[str, Any]) -> PartialPolicyDecision:
        config = rules_config.get("security", {})
        block_injection = config.get("block_prompt_injection", True)
        sensitive_keywords = config.get("sensitive_keywords", [])

        violations = []
        query = context.query.lower()

        # Prompt injection checks
        if block_injection:
            injection_patterns = [
                r"ignore previous instructions",
                r"system prompt",
                r"you must now act as",
                r"bypass safety filters",
            ]
            for pattern in injection_patterns:
                if re.search(pattern, query):
                    violations.append(f"Security violation: Potential prompt injection detected ('{pattern}').")

        # Sensitive keywords check
        for keyword in sensitive_keywords:
            if keyword.lower() in query:
                violations.append(f"Security violation: Query contains blocked keyword '{keyword}'.")

        return PartialPolicyDecision(
            violations=violations,
            reason="Security policy checks completed." if violations else None,
        )
