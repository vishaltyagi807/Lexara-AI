from __future__ import annotations

import logging

from core.graph.state import GraphState
from core.agents.policy.service import PolicyService

log = logging.getLogger(__name__)

_service = PolicyService()


def policy_agent_node(state: GraphState) -> GraphState:
    """LangGraph node: Evaluate routing policy constraints and update state."""
    # If upstream error exists, skip policy evaluation
    if state.get("error"):
        return state

    query = state.get("query", "")
    
    # Enrich metadata from GraphState
    metadata = {}
    intent = state.get("intent")
    if intent:
        metadata["query_type"] = intent.query_type
        metadata["complexity_score"] = intent.complexity_score
        metadata["execution_cost"] = intent.execution_cost
        metadata["requires_tools"] = intent.requires_tools
        if intent.requires_tools:
            # Check for requested tools
            metadata["requested_tools"] = ["web_search"]  # default fallback capability check

    # Evaluate routing policy
    decision = _service.evaluate_policy(query=query, metadata=metadata)
    
    log.info(
        "PolicyAgent: Evaluated policy version %d. Violations: %d",
        decision.policyVersion,
        len(decision.violations),
    )

    # Update state. If critical security violations occur, we can set an error.
    error = None
    if decision.violations:
        # Check if any violation contains 'security' or is critical enough to block
        security_violations = [v for v in decision.violations if "security" in v.lower() or "denied" in v.lower()]
        if security_violations:
            error = f"Blocked by policy: {security_violations[0]}"

    state_patch = {
        "policy_decision": decision,
    }
    if error:
        state_patch["error"] = error

    return {**state, **state_patch}
