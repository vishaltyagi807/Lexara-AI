"""agent_prompts.py — backward-compatibility shim.

AGENT_PROMPTS, FORMATTING_INSTRUCTIONS, and get_prompt_for() have moved to
core/prompts/response.py.
This file re-exports them so any existing code using:
    from core.models.agent_prompts import get_prompt_for
continues to work without changes.
"""
from core.prompts.response import (  # noqa: F401
    AGENT_PROMPTS,
    FORMATTING_INSTRUCTIONS,
    get_prompt_for,
)

__all__ = ["AGENT_PROMPTS", "FORMATTING_INSTRUCTIONS", "get_prompt_for"]