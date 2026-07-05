"""intent.py — re-exports the intent system prompt from the intent agent package.

Central lookup point: `from core.prompts.intent import INTENT_SYSTEM_PROMPT`
"""
from core.agents.intent.prompt import INTENT_SYSTEM_PROMPT  # noqa: F401

__all__ = ["INTENT_SYSTEM_PROMPT"]
