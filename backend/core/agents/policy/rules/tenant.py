from __future__ import annotations

from typing import Any
from core.agents.policy.rules import PolicyRule, PartialPolicyDecision
from core.agents.policy.schemas import EvaluationContext


class TenantRule(PolicyRule):
    def evaluate(self, context: EvaluationContext, rules_config: dict[str, Any]) -> PartialPolicyDecision:
        config = rules_config.get("tenant", {})
        allowed_tenants = config.get("allowed_tenants", [])
        blocked_ips = config.get("blocked_ips", [])

        violations = []
        if allowed_tenants and context.tenant_id:
            if context.tenant_id not in allowed_tenants:
                violations.append(f"Tenant '{context.tenant_id}' is not authorized to access the system.")

        if blocked_ips and context.client_ip:
            if context.client_ip in blocked_ips:
                violations.append(f"Access denied: Client IP '{context.client_ip}' is blocked by policy.")

        return PartialPolicyDecision(
            violations=violations,
            reason="Tenant and IP constraints checked." if violations else None,
        )
