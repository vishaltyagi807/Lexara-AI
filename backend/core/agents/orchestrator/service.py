"""service.py — OrchestratorService: business logic for query validation.

Responsibility
──────────────
The orchestrator is the first node in the pipeline. Its sole job is to:
  1. Sanitise the raw query string.
  2. Initialise all downstream state fields to known defaults.
  3. Reject empty/invalid queries early with a structured error.

No LLM is called here. No LangGraph imports.
"""
from __future__ import annotations

import logging

log = logging.getLogger(__name__)


class OrchestratorService:
    """Validates and prepares an incoming query before it enters the pipeline."""

    def prepare(self, raw_query: str) -> dict:
        """Sanitise the query and build the initial state patch.

        Args:
            raw_query: The raw user query string from GraphState.

        Returns:
            A dict containing the sanitised state fields.
            If the query is invalid, the 'error' key will be set.
        """
        query = (raw_query or "").strip()

        if not query:
            log.warning("OrchestratorService: empty query received.")
            return {
                "query": query,
                "intent": None,
                "routed_to": None,
                "agent_response": None,
                "error": "Empty query",
            }

        log.info("OrchestratorService: query accepted (%d chars)", len(query))
        return {
            "query": query,
            "intent": None,
            "routed_to": None,
            "agent_response": None,
            "error": None,
        }
