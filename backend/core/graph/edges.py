"""edges.py — conditional routing logic for the LangGraph pipeline.

Each function here is a conditional-edge selector: it inspects the current
GraphState and returns a string key that LangGraph uses to pick the next node.
"""
from core.graph.state import GraphState


def route_selector(state: GraphState) -> str:
    """Conditional edge: skip routing if there is a fatal error with no intent."""
    if state.get("error") and state.get("intent") is None:
        return "end"
    return "router"
