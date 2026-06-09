"""app.py — entrypoint and example execution."""
import logging
import json
import sys
import os

# Make imports work from repo root
sys.path.insert(0, os.path.dirname(__file__))

from config import cfg

logging.basicConfig(
    level=cfg.log_level,
    format="%(levelname)-8s %(name)s — %(message)s",
)

from graph import graph   # noqa: E402  (import after logging setup)


def run(query: str) -> dict:
    """Run the full intent-classification pipeline for a single query."""
    result = graph.invoke({"query": query})
    return {
        "query":          result["query"],
        "routed_to":      result.get("routed_to"),
        "agent_response": result.get("agent_response"),
        "error":          result.get("error"),
        "intent": result["intent"].model_dump() if result.get("intent") else None,
    }


EXAMPLE_QUERIES = [
    "Write a Python function to merge two sorted linked lists.",
    "What is the integral of x^2 * sin(x)?",
    "Explain why the sky is blue in simple terms.",
    "Summarise this article: [paste article here]",
    "Search the web for the latest LLM benchmarks and compare them.",
]


if __name__ == "__main__":
    print("Intent Router ready. Type your query (or 'exit' to quit)\n")
    while True:
        query = input("You: ").strip()
        if not query:
            continue
        if query.lower() in ("exit", "quit"):
            break
        output = run(query)
        print(json.dumps(output, indent=2))
        print()