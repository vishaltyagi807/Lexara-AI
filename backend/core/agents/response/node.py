"""node.py — ResponseNode: LangGraph node stub for the response agent.

Current status: STUB
────────────────────
The response agent is currently called directly from the API layer
(api/app/api/v1/chat/chat.py) and the CLI (core/app.py) via:
    ResponseService.stream_response(query, intent)

This file provides the LangGraph node wrapper for future graph integration
when the response step is moved into the LangGraph pipeline.

Future activation:
  1. Uncomment the node body below.
  2. Add the node to core/graph/builder.py.
  3. Update core/graph/edges.py routing accordingly.
"""
from __future__ import annotations

import logging

from core.graph.state import GraphState

log = logging.getLogger(__name__)


def response_node(state: GraphState) -> GraphState:
    """LangGraph node stub — response agent graph integration (future).

    When activated, this node will:
      1. Read query + intent from state.
      2. Call ResponseService.stream_response() or its async equivalent.
      3. Write agent_response back into state.
    """
    # Stub: response is currently generated outside the graph.
    # The state already contains agent_response from the router node.
    log.debug("ResponseNode: pass-through (response generated outside graph)")
    return state
