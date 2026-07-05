"""
conftest.py — Imported automatically by unittest discover before any tests run.
Ensures all SQLAlchemy ORM models are registered on the shared Base metadata so
that foreign-key references (e.g. conversations.user_id → users.id) can be
resolved without requiring the full FastAPI app to be loaded.
"""
from __future__ import annotations

# ── App models (must come first so Base metadata is populated) ────────────────
import app.models.user  # noqa: F401 – registers User / users table

# ── Core domain models ────────────────────────────────────────────────────────
import core.conversation.models  # noqa: F401 – registers Conversation / Message tables
import core.agents.policy.models  # noqa: F401 – registers Policy table
