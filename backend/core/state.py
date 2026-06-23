"""LangGraph shared state — typed, minimal, immutable-friendly."""
from typing import Optional
from typing_extensions import TypedDict

from core.models.intent import IntentResult


class GraphState(TypedDict):
    query: str
    intent: Optional[IntentResult]
    routed_to: Optional[str]
    agent_response: Optional[str]
    error: Optional[str]