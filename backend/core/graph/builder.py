"""builder.py — constructs and compiles the LangGraph StateGraph.

This module is the single place responsible for wiring all agent nodes and
edges into a compiled LangGraph. It does NOT hold any business logic itself.

To add a new agent:
  1. Import its node function here.
  2. Add g.add_node(...) and the relevant edges.
  3. That's it — no other file needs to change.
"""
from langgraph.graph import StateGraph, END

from core.graph.state import GraphState
from core.graph.edges import route_selector
from core.agents.orchestrator.node import orchestrator_node
from core.agents.intent.node import intent_agent_node
from core.agents.policy.node import policy_agent_node
from core.agents.router.node import router_node


def build_graph() -> StateGraph:
    """Wire all agent nodes into a compiled LangGraph StateGraph."""
    g = StateGraph(GraphState)

    # ── Nodes ─────────────────────────────────────────────────────────────────
    g.add_node("orchestrator", orchestrator_node)
    g.add_node("intent_agent", intent_agent_node)
    g.add_node("policy_agent", policy_agent_node)
    g.add_node("router",       router_node)

    # ── Entry point ───────────────────────────────────────────────────────────
    g.set_entry_point("orchestrator")

    # ── Edges ─────────────────────────────────────────────────────────────────
    g.add_edge("orchestrator", "intent_agent")

    g.add_conditional_edges(
        "intent_agent",
        route_selector,
        {"policy_agent": "policy_agent", "end": END},
    )
    g.add_edge("policy_agent", "router")
    g.add_edge("router", END)

    return g.compile()
