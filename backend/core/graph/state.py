from typing import Optional, Any
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
    chat_history: Optional[list[Any]]
    summary: Optional[str]
