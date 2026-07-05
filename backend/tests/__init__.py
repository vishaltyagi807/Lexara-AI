"""tests — Lexara AI backend test suite.

This __init__.py is executed by `unittest discover` before any test module is
loaded.  We import all SQLAlchemy ORM models here so that foreign-key references
(e.g. conversations.user_id → users.id) are registered on the shared Base
metadata before any mapper tries to resolve them.
"""
from __future__ import annotations

# ── Must import all ORM models before any test session begins ─────────────────
import app.models.user  # noqa: F401  –  registers User / users table
import core.conversation.models  # noqa: F401  –  registers Conversation / Message
import core.agents.policy.repository  # noqa: F401  –  registers RoutingPolicy table
