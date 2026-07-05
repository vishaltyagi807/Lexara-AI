"""base_agent.py — abstract base class that every Lexara AI agent must implement.

Design contract
───────────────
Every agent in the Lexara AI pipeline:
  1. Receives the current LangGraph GraphState.
  2. Performs its focused responsibility (classify, route, guard, respond …).
  3. Returns an updated GraphState (partial dict is fine — LangGraph merges it).

Usage
─────
    from core.interfaces.base_agent import BaseAgent
    from core.graph.state import GraphState

    class MyAgent(BaseAgent):
        async def run(self, state: GraphState) -> GraphState:
            # ... business logic ...
            return {**state, "my_field": result}
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.graph.state import GraphState


class BaseAgent(ABC):
    """Abstract interface for all Lexara AI agents.

    Subclasses must implement `run()`. Synchronous node wrappers may call
    `asyncio.run(agent.run(state))` when LangGraph executes them in a sync
    context, or use `async def node_fn()` with `await agent.run(state)` for
    async graphs.
    """

    @abstractmethod
    async def run(self, state: "GraphState") -> "GraphState":
        """Execute this agent's logic and return the updated graph state.

        Args:
            state: The current LangGraph GraphState dict.

        Returns:
            An updated GraphState. Must contain at minimum all keys present in
            the input state; new keys may be added.
        """
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
