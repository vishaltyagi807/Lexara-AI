"""app.py — entrypoint. Classifies intent then streams the response."""
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config import cfg

logging.basicConfig(
    level=cfg.log_level,
    format="%(levelname)-8s %(name)s — %(message)s",
)

from graph import graph
from nodes.response_agent import stream_response


def run(query: str) -> None:
    """Classify intent, then stream the agent response."""
    result = graph.invoke({"query": query})
    intent = result.get("intent")

    if result.get("error") and intent is None:
        print(f"\nError: {result['error']}")
        return

    # Show routing info
    print(f"\n[{intent.query_type.upper()} | complexity={intent.complexity_score} | cost={intent.execution_cost}]")

    # Stream the actual response
    stream_response(query, intent)


if __name__ == "__main__":
    print("Lexara AI ready. Type your query (or 'exit' to quit)\n")
    while True:
        query = input("You: ").strip()
        if not query:
            continue
        if query.lower() in ("exit", "quit"):
            print("Bye!")
            break
        run(query)