"""node.py — OrchestratorNode: LangGraph integration for the orchestrator agent.

Responsibility
──────────────
This module is the thin LangGraph boundary layer. It:
  1. Reads the raw query from GraphState.
  2. Delegates all logic to OrchestratorService.
  3. Returns the updated GraphState.

No business logic lives here.
"""
from __future__ import annotations

import logging

from core.graph.state import GraphState
from core.agents.orchestrator.service import OrchestratorService

log = logging.getLogger(__name__)

_service = OrchestratorService()


def orchestrator_node(state: GraphState) -> GraphState:
    """LangGraph node: sanitise input and initialise state fields."""
    patch = _service.prepare(raw_query=state.get("query", ""))
    return {**state, **patch}
