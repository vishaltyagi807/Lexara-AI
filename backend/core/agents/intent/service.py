"""service.py — IntentService: business logic for intent classification.

Responsibility
──────────────
  1. Build and cache the LangChain-Groq structured-output chain.
  2. Invoke the chain with the user query.
  3. Return an IntentResult or a safe fallback on failure.

No LangGraph state handling lives here.
"""
from __future__ import annotations

import logging
from functools import lru_cache

from langchain_groq import ChatGroq

from core.config import cfg
from core.models.intent import IntentResult
from core.agents.intent.prompt import INTENT_SYSTEM_PROMPT

log = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_chain():
    """Lazy-init — build once, share across all requests."""
    llm = ChatGroq(
        model=cfg.model_name,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
    )
    return llm.with_structured_output(IntentResult)


class IntentService:
    """Classifies a user query into a structured IntentResult."""

    def classify(self, query: str) -> tuple[IntentResult, str | None]:
        """Run intent classification against the configured LLM.

        Args:
            query: The sanitised user query string.

        Returns:
            A tuple of (IntentResult, error_string | None).
            On success, error is None.
            On failure, a fallback IntentResult is returned with error set.
        """
        log.info("IntentService classifying: %.80s…", query)

        try:
            chain = _get_chain()
            result: IntentResult = chain.invoke([
                {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                {"role": "user",   "content": query},
            ])
            log.info(
                "Intent → type=%s complexity=%d cost=%s confidence=%.2f",
                result.query_type, result.complexity_score,
                result.execution_cost, result.confidence,
            )
            return result, None

        except Exception as exc:
            log.error("IntentService failed: %s", exc)
            fallback = IntentResult(
                query_type="unknown",
                complexity_score=5,
                confidence=0.0,
                execution_cost="medium",
                requires_tools=False,
                recommended_agent="GeneralAgent",
                reasoning=f"Classification failed: {exc}",
            )
            return fallback, str(exc)
