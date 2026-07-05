from __future__ import annotations

import logging
from typing import Any

from core.agents.policy.cache import PolicyCache
from core.agents.policy.engine import PolicyEngine
from core.agents.policy.decision import PolicyDecision
from core.agents.policy.schemas import EvaluationContext

log = logging.getLogger(__name__)


class PolicyService:
    def __init__(self) -> None:
        self.engine = PolicyEngine()
        self.cache = PolicyCache()

    def evaluate_policy(self, query: str, metadata: dict[str, Any] | None = None) -> PolicyDecision:
        """Run routing policy checks against the current cached active policy."""
        meta = metadata or {}
        
        # 1. Fetch active policy rules configuration from cache
        active_rules = self.cache.get_active_policy()
        version = self.cache.current_version() or 0

        # If cache is not initialized, run with an empty rule set or default rules
        if active_rules is None:
            log.warning("PolicyService: No active policy found in cache. Using empty rule set.")
            active_rules = {}

        # 2. Extract context attributes from request metadata
        user_id = meta.get("user_id")
        tenant_id = meta.get("tenant_id")
        client_ip = meta.get("client_ip")
        current_budget = meta.get("current_budget_spent")
        current_latency = meta.get("current_latency_ms")
        required_capabilities = meta.get("required_capabilities", [])

        context = EvaluationContext(
            query=query,
            user_id=user_id,
            tenant_id=tenant_id,
            current_budget_spent=current_budget,
            current_latency_ms=current_latency,
            required_capabilities=required_capabilities,
            client_ip=client_ip,
            metadata=meta,
        )

        # 3. Evaluate context against rules
        log.info("PolicyService: Evaluating rules context for version %d", version)
        decision = self.engine.evaluate(context, active_rules, version)
        return decision
