from __future__ import annotations

import logging
from typing import Any

from core.agents.policy.decision import PolicyDecision
from core.agents.policy.schemas import EvaluationContext
from core.agents.policy.rules import PolicyRule, PartialPolicyDecision

# Import all rules
from core.agents.policy.rules.provider import ProviderRule
from core.agents.policy.rules.budget import BudgetRule
from core.agents.policy.rules.latency import LatencyRule
from core.agents.policy.rules.availability import AvailabilityRule
from core.agents.policy.rules.reasoning import ReasoningRule
from core.agents.policy.rules.tools import ToolsRule
from core.agents.policy.rules.rag import RagRule
from core.agents.policy.rules.tenant import TenantRule
from core.agents.policy.rules.security import SecurityRule

log = logging.getLogger(__name__)


class PolicyEngine:
    def __init__(self) -> None:
        self.rules: list[PolicyRule] = [
            ProviderRule(),
            BudgetRule(),
            LatencyRule(),
            AvailabilityRule(),
            ReasoningRule(),
            ToolsRule(),
            RagRule(),
            TenantRule(),
            SecurityRule(),
        ]

    def evaluate(self, context: EvaluationContext, rules_config: dict[str, Any], policy_version: int) -> PolicyDecision:
        """Evaluate all rules and merge their partial decisions into a final PolicyDecision."""
        partial_decisions: list[PartialPolicyDecision] = []

        for rule in self.rules:
            try:
                decision = rule.evaluate(context, rules_config)
                partial_decisions.append(decision)
            except Exception as exc:
                log.error("PolicyEngine: Rule %s failed to evaluate: %s", rule.__class__.__name__, exc)
                # Keep executing other rules, record evaluation failure
                partial_decisions.append(
                    PartialPolicyDecision(
                        violations=[f"Rule failure: {rule.__class__.__name__} errored during evaluation."]
                    )
                )

        return self.merge_decisions(partial_decisions, policy_version)

    def merge_decisions(self, partials: list[PartialPolicyDecision], version: int) -> PolicyDecision:
        """Merge a list of PartialPolicyDecision objects into a single PolicyDecision."""
        allowed_providers: set[str] | None = None
        blocked_providers: set[str] = set()
        preferred_providers: set[str] = set()
        preferred_capabilities: set[str] = set()
        
        max_budget: float | None = None
        max_latency: float | None = None
        
        allow_streaming = True
        allow_caching = True
        allow_reasoning = True
        allow_rag = True
        
        allowed_tools: set[str] | None = None
        max_tokens: int | None = None
        routing_priority = "normal"
        routing_hints: dict[str, Any] = {}
        violations: list[str] = []
        reasons: list[str] = []
        min_confidence = 1.0

        for p in partials:
            # Union of violations
            if p.violations:
                violations.extend(p.violations)

            # Allowed providers (Intersection of all defined constraints)
            if p.allowedProviders is not None:
                p_allowed = set(p.allowedProviders)
                if allowed_providers is None:
                    allowed_providers = p_allowed
                else:
                    allowed_providers = allowed_providers.intersection(p_allowed)

            # Blocked providers (Union)
            if p.blockedProviders:
                blocked_providers.update(p.blockedProviders)

            # Preferred providers (Union)
            if p.preferredProviders:
                preferred_providers.update(p.preferredProviders)

            # Preferred capabilities (Union)
            if p.preferredCapabilities:
                preferred_capabilities.update(p.preferredCapabilities)

            # Numeric minimums / maximums
            if p.maxBudget is not None:
                max_budget = min(max_budget, p.maxBudget) if max_budget is not None else p.maxBudget

            if p.maxLatency is not None:
                max_latency = min(max_latency, p.maxLatency) if max_latency is not None else p.maxLatency

            if p.maxTokens is not None:
                max_tokens = min(max_tokens, p.maxTokens) if max_tokens is not None else p.maxTokens

            # Booleans (Logical AND)
            if p.allowStreaming is not None:
                allow_streaming = allow_streaming and p.allowStreaming

            if p.allowCaching is not None:
                allow_caching = allow_caching and p.allowCaching

            if p.allowReasoning is not None:
                allow_reasoning = allow_reasoning and p.allowReasoning

            if p.allowRAG is not None:
                allow_rag = allow_rag and p.allowRAG

            # Allowed tools (Intersection)
            if p.allowedTools is not None:
                p_tools = set(p.allowedTools)
                if allowed_tools is None:
                    allowed_tools = p_tools
                else:
                    allowed_tools = allowed_tools.intersection(p_tools)

            # Routing priority resolver
            if p.routingPriority is not None:
                # Priority hierarchy: high > normal > low
                if p.routingPriority == "high":
                    routing_priority = "high"
                elif p.routingPriority == "normal" and routing_priority != "high":
                    routing_priority = "normal"
                elif p.routingPriority == "low" and routing_priority not in ("high", "normal"):
                    routing_priority = "low"

            # Merge routing hints dict
            if p.routingHints:
                routing_hints.update(p.routingHints)

            # Append reason
            if p.reason:
                reasons.append(p.reason)

            # Confidence (Minimum)
            if p.confidence is not None:
                min_confidence = min(min_confidence, p.confidence)

        # Filter out blocked providers from preferred
        pref_providers_list = [p for p in preferred_providers if p not in blocked_providers]

        # Convert sets back to lists
        allowed_providers_list = list(allowed_providers) if allowed_providers is not None else []
        blocked_providers_list = list(blocked_providers)
        preferred_capabilities_list = list(preferred_capabilities)
        allowed_tools_list = list(allowed_tools) if allowed_tools is not None else []

        reason_str = "; ".join(reasons) if reasons else "Policy evaluated successfully."

        return PolicyDecision(
            allowedProviders=allowed_providers_list,
            blockedProviders=blocked_providers_list,
            preferredProviders=pref_providers_list,
            preferredCapabilities=preferred_capabilities_list,
            maxBudget=max_budget,
            maxLatency=max_latency,
            allowStreaming=allow_streaming,
            allowCaching=allow_caching,
            allowReasoning=allow_reasoning,
            allowRAG=allow_rag,
            allowedTools=allowed_tools_list,
            maxTokens=max_tokens,
            routingPriority=routing_priority,
            routingHints=routing_hints,
            violations=violations,
            reason=reason_str,
            confidence=min_confidence,
            policyVersion=version,
        )
