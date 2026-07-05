from __future__ import annotations

import logging
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from core.config import cfg

log = logging.getLogger(__name__)

SUMMARIZER_PROMPT = (
    "You are a conversation summarizer. Summarize the key points, decisions, and context "
    "of the conversation messages provided below. Be extremely concise, factual, and clear (max 200 words). "
    "If a prior summary is provided, synthesize the new context and merge it with the prior summary."
)


class ConversationSummarizer:
    def __init__(self) -> None:
        self.llm = ChatGroq(
            model=cfg.model_name,
            temperature=cfg.temperature,
            max_tokens=400,
        )

    async def summarize(self, messages_content: str, prior_summary: str | None = None) -> str:
        """Asynchronously summarize a block of messages, combining it with any prior summary."""
        log.info("ConversationSummarizer: Summarizing conversation history...")
        try:
            prompt_content = ""
            if prior_summary:
                prompt_content += f"Prior Summary:\n{prior_summary}\n\n"
            prompt_content += f"New Messages to Summarize:\n{messages_content}"

            messages = [
                SystemMessage(content=SUMMARIZER_PROMPT),
                HumanMessage(content=prompt_content),
            ]
            response = await self.llm.ainvoke(messages)
            summary = response.content.strip()
            log.info("ConversationSummarizer: Summarization complete (%d chars)", len(summary))
            return summary
        except Exception as exc:
            log.error("ConversationSummarizer: Failed to summarize: %s", exc)
            return prior_summary or ""
