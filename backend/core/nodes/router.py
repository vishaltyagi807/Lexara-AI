"""Router — dispatches to the correct downstream agent node."""
import logging
from core.config import cfg
from core.models.intent import IntentResult
from core.state import GraphState

log = logging.getLogger(__name__)


def coding_agent(query: str, intent: IntentResult) -> str:
    return f"[CodingAgent] Processing: {query[:60]}… (complexity={intent.complexity_score})"

def math_agent(query: str, intent: IntentResult) -> str:
    return f"[MathAgent] Solving: {query[:60]}…"

def reasoning_agent(query: str, intent: IntentResult) -> str:
    return f"[ReasoningAgent] Reasoning over: {query[:60]}…"

def research_agent(query: str, intent: IntentResult) -> str:
    return f"[ResearchAgent] Researching: {query[:60]}…"

def data_analysis_agent(query: str, intent: IntentResult) -> str:
    return f"[DataAnalysisAgent] Analysing: {query[:60]}…"

def general_agent(query: str, intent: IntentResult) -> str:
    return f"[GeneralAgent] Handling: {query[:60]}…"


_AGENT_REGISTRY: dict = {
    "CodingAgent":       coding_agent,
    "MathAgent":         math_agent,
    "ReasoningAgent":    reasoning_agent,
    "ResearchAgent":     research_agent,
    "DataAnalysisAgent": data_analysis_agent,
    "GeneralAgent":      general_agent,
}


def router_node(state: GraphState) -> GraphState:
    """Route to the correct agent based on IntentResult."""
    intent: IntentResult = state["intent"]
    query:  str          = state["query"]

    agent_label = (
        intent.recommended_agent
        if intent.recommended_agent in _AGENT_REGISTRY
        else cfg.routing_map.get(intent.query_type, "GeneralAgent")
    )

    log.info("Router → %s", agent_label)
    agent_fn = _AGENT_REGISTRY.get(agent_label, general_agent)
    response  = agent_fn(query, intent)

    return {**state, "routed_to": agent_label, "agent_response": response}


def route_selector(state: GraphState) -> str:
    """Conditional edge: skip routing if there is a fatal error."""
    if state.get("error") and state.get("intent") is None:
        return "end"
    return "router"