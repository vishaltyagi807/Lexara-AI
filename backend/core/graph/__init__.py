"""core/graph/__init__.py — public re-exports for the graph package.

Importing `from core.graph import graph` or `from core.graph import build_graph`
works identically to the old `from core.graph import graph` import path.
"""
from core.graph.graph import graph  # noqa: F401 — re-export compiled graph
from core.graph.builder import build_graph  # noqa: F401 — re-export builder

__all__ = ["graph", "build_graph"]
