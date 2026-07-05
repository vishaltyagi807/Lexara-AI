"""node.py — RouterNode: LangGraph integration for the router agent.

Responsibility
──────────────
This module is the thin LangGraph boundary layer. It:
  1. Reads the intent and query from GraphState.
  2. Delegates all dispatch logic to RouterService.
  3. Writes agent_label and agent_response back into GraphState.

No business logic lives here.
"""
from __future__ import annotations

import logging

from core.graph.state import GraphState
from core.agents.router.service import RouterService

log = logging.getLogger(__name__)

_service = RouterService()


def router_node(state: GraphState) -> GraphState:
    """LangGraph node: route to the correct agent based on IntentResult."""
    intent = state["intent"]
    query  = state["query"]

    agent_label, response = _service.dispatch(query=query, intent=intent)

    return {**state, "routed_to": agent_label, "agent_response": response}
