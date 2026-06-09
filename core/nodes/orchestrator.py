"""OrchestratorNode — validates and prepares the incoming query."""
import logging
from state import GraphState

log = logging.getLogger(__name__)


def orchestrator_node(state: GraphState) -> GraphState:
    """Sanitise input and initialise state fields."""
    query = (state.get("query") or "").strip()
    if not query:
        log.warning("Empty query received.")
        return {**state, "error": "Empty query", "query": query}

    log.info("Orchestrator received query (%d chars)", len(query))
    return {
        **state,
        "query": query,
        "intent": None,
        "routed_to": None,
        "agent_response": None,
        "error": None,
    }