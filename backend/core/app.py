"""app.py — CLI entrypoint. Classifies intent then streams the response."""
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core.config import cfg
from core.graph import graph
from core.agents.response.service import ResponseService

logging.basicConfig(
    level=cfg.log_level,
    format="%(levelname)-8s %(name)s — %(message)s",
)

_response_service = ResponseService()


def run(query: str) -> None:
    result = graph.invoke({"query": query})
    intent = result.get("intent")

    if result.get("error") and intent is None:
        print(f"\nError: {result['error']}")
        return

    print(f"\n[{intent.query_type.upper()} | complexity={intent.complexity_score} | cost={intent.execution_cost}]")
    _response_service.stream_response(query, intent)


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