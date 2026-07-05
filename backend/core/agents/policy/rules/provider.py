from __future__ import annotations

from typing import Any
from core.agents.policy.rules import PolicyRule, PartialPolicyDecision
from core.agents.policy.schemas import EvaluationContext


class ProviderRule(PolicyRule):
    def evaluate(self, context: EvaluationContext, rules_config: dict[str, Any]) -> PartialPolicyDecision:
        config = rules_config.get("provider", {})
        allowed = config.get("allowed_providers")
        blocked = config.get("blocked_providers")
        preferred = config.get("preferred_providers")

        violations = []
        # If context already specifies a target provider, check if it's allowed/blocked
        if context.provider:
            prov = context.provider.lower()
            if allowed and prov not in [a.lower() for a in allowed]:
                violations.append(f"Provider '{context.provider}' is not in the allowed list.")
            if blocked and prov in [b.lower() for b in blocked]:
                violations.append(f"Provider '{context.provider}' is blocked by policy.")

        return PartialPolicyDecision(
            allowedProviders=allowed,
            blockedProviders=blocked,
            preferredProviders=preferred,
            violations=violations,
            reason="Checked allowed/blocked/preferred providers." if violations else None,
        )
