"""response_agent.py — streams the final response to the user."""
import logging
from functools import lru_cache

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from core.models.intent import IntentResult
from core.models.model_registry import get_model_for
from core.models.agent_prompts import get_prompt_for
from core.config import cfg

log = logging.getLogger(__name__)


@lru_cache(maxsize=16)
def _get_llm(model_name: str) -> ChatGroq:
    log.info("Initialising LLM: %s", model_name)
    return ChatGroq(
        model=model_name,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
    )


def stream_response(query: str, intent: IntentResult) -> str:
    """Stream the agent response to stdout, return full text when done."""
    model_name    = get_model_for(intent.query_type)
    system_prompt = get_prompt_for(intent.query_type)
    llm           = _get_llm(model_name)

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

    print("\n")
    return full_response