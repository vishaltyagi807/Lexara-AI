"""graph.py — compiled LangGraph singleton.

This module holds the single compiled graph instance used across the
entire application. Import via `from core.graph import graph`.
"""
from core.graph.builder import build_graph

graph = build_graph()
