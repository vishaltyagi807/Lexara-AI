"""service.py — RouterService: business logic for agent dispatch.

Responsibility
──────────────
  1. Resolve the correct agent label from IntentResult and the routing config.
  2. Look up the agent strategy function from the registry.
  3. Invoke the strategy and return (agent_label, response).

No LangGraph state handling lives here.
"""
from __future__ import annotations

import logging

from core.config import cfg
from core.models.intent import IntentResult
from core.agents.router.strategies import _AGENT_REGISTRY, general_agent

log = logging.getLogger(__name__)


class RouterService:
    """Dispatches a query to the correct downstream agent strategy."""

    def dispatch(self, query: str, intent: IntentResult) -> tuple[str, str]:
        """Resolve the agent, call its strategy, and return the result.

        Args:
            query:  The sanitised user query string.
            intent: The IntentResult produced by the IntentAgent.

        Returns:
            A tuple of (agent_label, agent_response_string).
        """
        # Prefer intent.recommended_agent if it's registered; fall back to
        # the config routing_map, then hard-fallback to GeneralAgent.
        if intent.recommended_agent in _AGENT_REGISTRY:
            agent_label = intent.recommended_agent
        else:
            agent_label = cfg.routing_map.get(intent.query_type, "GeneralAgent")

        log.info("RouterService → %s", agent_label)

        agent_fn = _AGENT_REGISTRY.get(agent_label, general_agent)
        response = agent_fn(query, intent)

        return agent_label, response
