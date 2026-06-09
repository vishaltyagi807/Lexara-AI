"""IntentAgent — classifies the query into a structured IntentResult."""
import logging
from functools import lru_cache

from langchain_groq import ChatGroq

from config import cfg
from models.intent import IntentResult
from state import GraphState

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an intent classification engine.
Analyse the user query and return a structured classification.

Guidelines:
- complexity_score: 1 (trivial) → 10 (expert-level multi-step)
- confidence: how certain you are about the classification (0-1)
- execution_cost: low (<1s), medium (1-5s), high (>5s or tool-heavy)
- requires_tools: true if web search, code execution, APIs, or DB access needed
- recommended_agent: the best specialist agent name for this query
- reasoning: one concise sentence explaining your classification
"""


@lru_cache(maxsize=1)
def _get_chain():
    """Lazy-init — instantiated once, shared across calls."""
    llm = ChatGroq(
        model=cfg.model_name,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
    )
    return llm.with_structured_output(IntentResult)


def intent_agent_node(state: GraphState) -> GraphState:
    """Classify the query; write IntentResult into state."""
    if state.get("error"):
        return state  # propagate upstream errors

    query = state["query"]
    log.info("IntentAgent classifying: %.80s…", query)

    try:
        chain = _get_chain()
        result: IntentResult = chain.invoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": query},
        ])
        log.info(
            "Intent → type=%s complexity=%d cost=%s confidence=%.2f",
            result.query_type, result.complexity_score,
            result.execution_cost, result.confidence,
        )
        return {**state, "intent": result}

    except Exception as exc:
        log.error("IntentAgent failed: %s", exc)
        # Graceful fallback — route to GeneralAgent
        fallback = IntentResult(
            query_type="unknown",
            complexity_score=5,
            confidence=0.0,
            execution_cost="medium",
            requires_tools=False,
            recommended_agent="GeneralAgent",
            reasoning=f"Classification failed: {exc}",
        )
        return {**state, "intent": fallback, "error": str(exc)}