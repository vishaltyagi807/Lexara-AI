"""response_agent.py — streams the final response to the user.

One LLM call per query, model and prompt selected by query_type.
Streams token by token so it feels like a real conversation.
"""
import logging
from functools import lru_cache

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from models.intent import IntentResult
from models.model_registry import get_model_for
from models.agent_prompts import get_prompt_for
from config import cfg

log = logging.getLogger(__name__)


@lru_cache(maxsize=16)
def _get_llm(model_name: str) -> ChatGroq:
    """One cached LLM instance per model — avoids re-initialising on every call."""
    log.info("Initialising LLM: %s", model_name)
    return ChatGroq(
        model=model_name,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
    )


def stream_response(query: str, intent: IntentResult) -> str:
    """Stream the agent response to stdout, return full text when done."""

    model_name  = get_model_for(intent.query_type)
    system_prompt = get_prompt_for(intent.query_type)
    llm = _get_llm(model_name)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query),
    ]

    log.info(
        "ResponseAgent → model=%s type=%s complexity=%d",
        model_name, intent.query_type, intent.complexity_score,
    )

    print(f"\nAssistant: ", end="", flush=True)

    full_response = ""
    try:
        for chunk in llm.stream(messages):
            token = chunk.content
            print(token, end="", flush=True)
            full_response += token
    except Exception as exc:
        log.error("ResponseAgent streaming failed: %s", exc)
        fallback = "Sorry, I encountered an error generating a response."
        print(fallback, end="", flush=True)
        full_response = fallback

    print("\n")  # newline after stream ends
    return full_response