from __future__ import annotations

from typing import Any
from core.agents.policy.rules import PolicyRule, PartialPolicyDecision
from core.agents.policy.schemas import EvaluationContext


class RagRule(PolicyRule):
    def evaluate(self, context: EvaluationContext, rules_config: dict[str, Any]) -> PartialPolicyDecision:
        config = rules_config.get("rag", {})
        allow_rag = config.get("allow_rag", True)
        force_rag_types = config.get("force_rag_for_query_types", [])

        violations = []
        if "rag" in context.required_capabilities and not allow_rag:
            violations.append("RAG capability is disabled by policy.")

        query_type = context.metadata.get("query_type")
        force_rag = False
        if allow_rag and query_type in force_rag_types:
            force_rag = True

        hints = {}
        if force_rag:
            hints["force_rag"] = True

        return PartialPolicyDecision(
            allowRAG=allow_rag,
            routingHints=hints if hints else None,
            violations=violations,
            reason="RAG policy evaluated." if violations else None,
        )
