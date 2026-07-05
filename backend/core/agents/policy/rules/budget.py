from __future__ import annotations

from typing import Any
from core.agents.policy.rules import PolicyRule, PartialPolicyDecision
from core.agents.policy.schemas import EvaluationContext


class BudgetRule(PolicyRule):
    def evaluate(self, context: EvaluationContext, rules_config: dict[str, Any]) -> PartialPolicyDecision:
        config = rules_config.get("budget", {})
        max_budget = config.get("max_budget_per_request")

        violations = []
        if max_budget is not None and context.current_budget_spent is not None:
            if context.current_budget_spent > max_budget:
                violations.append(
                    f"Current budget spent ({context.current_budget_spent}) exceeds max allowed per request ({max_budget})."
                )

        return PartialPolicyDecision(
            maxBudget=max_budget,
            violations=violations,
            reason="Budget constraints checked." if violations else None,
        )
