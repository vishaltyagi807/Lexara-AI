"""strategies.py — agent dispatch strategies and the agent registry.

Each strategy function is a callable that receives (query, intent) and returns
a routing decision string. The _AGENT_REGISTRY maps agent label strings to
their strategy functions.

To add a new downstream agent:
  1. Add a new strategy function below.
  2. Register it in _AGENT_REGISTRY.
  3. That's it — RouterService.dispatch() will pick it up automatically.
"""
from __future__ import annotations

from core.models.intent import IntentResult


# ── Strategy functions ────────────────────────────────────────────────────────
# Each function is a stub today. Replace with real agent invocation logic
# when specialist agents are implemented.

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


# ── Agent registry ────────────────────────────────────────────────────────────
# Maps agent label (str) → strategy callable.
# Used by RouterService.dispatch() for O(1) lookup.
AgentStrategy = type(general_agent)  # type alias for readability

_AGENT_REGISTRY: dict[str, AgentStrategy] = {
    "CodingAgent":       coding_agent,
    "MathAgent":         math_agent,
    "ReasoningAgent":    reasoning_agent,
    "ResearchAgent":     research_agent,
    "DataAnalysisAgent": data_analysis_agent,
    "GeneralAgent":      general_agent,
}
