"""node.py — IntentAgentNode: LangGraph integration for intent classification.

Responsibility
──────────────
This module is the thin LangGraph boundary layer. It:
  1. Guards against forwarding a pre-existing error state.
  2. Reads the query from GraphState.
  3. Delegates all classification logic to IntentService.
  4. Writes the result back into GraphState.

No business logic lives here.
"""
from __future__ import annotations

import logging

from core.graph.state import GraphState
from core.agents.intent.service import IntentService

log = logging.getLogger(__name__)

_service = IntentService()


def intent_agent_node(state: GraphState) -> GraphState:
    """LangGraph node: classify the query; write IntentResult into state."""
    if state.get("error"):
        # Fatal upstream error — skip classification and propagate state.
        return state

    query = state["query"]
    intent, error = _service.classify(query)

    return {**state, "intent": intent, "error": error}
