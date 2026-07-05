from __future__ import annotations

import logging
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from core.config import cfg

log = logging.getLogger(__name__)

TITLE_PROMPT = (
    "You are a conversation title generator. Analyze the user's first query and "
    "generate a concise, natural, and engaging title (4 to 6 words maximum) "
    "summarizing the topic. Do NOT write quotes, markdown syntax, or explain the title. "
    "Just output the raw title text."
)


class TitleGenerator:
    def __init__(self) -> None:
        self.llm = ChatGroq(
            model=cfg.model_name,
            temperature=0.7,  # higher temperature for natural title selection
            max_tokens=50,
        )

    async def generate_title(self, query: str) -> str:
        """Asynchronously generate a title from the user query."""
        log.info("TitleGenerator: Generating title for query: %.50s...", query)
        try:
            messages = [
                SystemMessage(content=TITLE_PROMPT),
                HumanMessage(content=query),
            ]
            response = await self.llm.ainvoke(messages)
            title = response.content.strip().strip('"').strip("'")
            log.info("TitleGenerator: Generated title: '%s'", title)
            return title
        except Exception as exc:
            log.error("TitleGenerator: Failed to generate title: %s", exc)
            return "New Conversation"
