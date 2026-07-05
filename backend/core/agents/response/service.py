"""service.py — ResponseService: business logic for streaming LLM responses.

Responsibility
──────────────
  1. Resolve the correct model and system prompt from the intent.
  2. Build (and cache) the LLM instance.
  3. Stream the response token-by-token.

Currently called directly from the API layer (chat.py) and the CLI (app.py).
Future: integrate as a LangGraph node for end-to-end graph execution.
"""
from __future__ import annotations

import logging
from functools import lru_cache

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from core.config import cfg
from core.models.intent import IntentResult
from core.registry.model_registry import get_model_for
from core.prompts.response import get_prompt_for

log = logging.getLogger(__name__)


@lru_cache(maxsize=16)
def _get_llm(model_name: str) -> ChatGroq:
    """Return a cached ChatGroq instance for the given model name."""
    log.info("ResponseService: initialising LLM %s", model_name)
    return ChatGroq(
        model=model_name,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
    )


class ResponseService:
    """Generates and streams the final LLM response for a classified query."""

    def stream_response(self, query: str, intent: IntentResult) -> str:
        """Stream the agent response to stdout; return the full text when done.

        Args:
            query:  The sanitised user query string.
            intent: The IntentResult used to select model and prompt.

        Returns:
            The complete response text as a single string.
        """
        model_name    = get_model_for(intent.query_type)
        system_prompt = get_prompt_for(intent.query_type)
        llm           = _get_llm(model_name)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query),
        ]

        log.info(
            "ResponseService → model=%s type=%s complexity=%d",
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
            log.error("ResponseService streaming failed: %s", exc)
            fallback = "Sorry, I encountered an error generating a response."
            print(fallback, end="", flush=True)
            full_response = fallback

        print("\n")
        return full_response
