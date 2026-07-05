"""state.py — backward-compatibility shim.

GraphState has moved to core/graph/state.py.
This file re-exports it so any existing code using:
    from core.state import GraphState
continues to work without changes.
"""
from core.graph.state import GraphState  # noqa: F401

__all__ = ["GraphState"]