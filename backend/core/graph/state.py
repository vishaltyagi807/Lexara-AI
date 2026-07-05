"""state.py — LangGraph shared state: typed, minimal, immutable-friendly."""
from typing import Optional
from typing_extensions import TypedDict

from core.models.intent import IntentResult
from core.agents.policy.decision import PolicyDecision


class GraphState(TypedDict):
    query: str
    intent: Optional[IntentResult]
    routed_to: Optional[str]
    agent_response: Optional[str]
    error: Optional[str]
    policy_decision: Optional[PolicyDecision]
