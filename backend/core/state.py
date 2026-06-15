"""LangGraph shared state — typed, minimal, immutable-friendly."""
from typing import Optional
from typing_extensions import TypedDict

from models.intent import IntentResult


class GraphState(TypedDict):
    query: str                            # raw user input
    intent: Optional[IntentResult]        # filled by IntentAgent
    routed_to: Optional[str]             # filled by Router
    agent_response: Optional[str]        # filled by downstream agent
    error: Optional[str]                 # set on failure