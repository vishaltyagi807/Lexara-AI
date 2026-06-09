"""graph.py — wires all nodes into a LangGraph StateGraph."""
from langgraph.graph import StateGraph, END

from state import GraphState
from nodes.orchestrator import orchestrator_node
from nodes.intent_agent  import intent_agent_node
from nodes.router        import router_node, route_selector


def build_graph() -> StateGraph:
    g = StateGraph(GraphState)

    g.add_node("orchestrator", orchestrator_node)
    g.add_node("intent_agent", intent_agent_node)
    g.add_node("router",       router_node)

    g.set_entry_point("orchestrator")
    g.add_edge("orchestrator", "intent_agent")

    # Conditional: if fatal error skip routing, else go to router
    g.add_conditional_edges(
        "intent_agent",
        route_selector,
        {"router": "router", "end": END},
    )
    g.add_edge("router", END)

    return g.compile()


# Module-level singleton — import and call directly
graph = build_graph()
