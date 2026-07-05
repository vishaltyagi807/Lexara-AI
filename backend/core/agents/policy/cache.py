from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

log = logging.getLogger(__name__)


class PolicyCache:
    _instance: Optional[PolicyCache] = None

    def __new__(cls, *args, **kwargs) -> PolicyCache:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._active_policy = None
            cls._instance._version = None
            cls._instance._last_updated = None
            cls._instance._reload_count = 0
            cls._instance._hits = 0
            cls._instance._misses = 0
        return cls._instance

    def get_active_policy(self) -> Optional[dict]:
        """Fetch the current active policy payload."""
        if self._active_policy is None:
            self._misses += 1
            return None
        self._hits += 1
        return self._active_policy

    def current_version(self) -> Optional[int]:
        """Fetch the version of the active policy."""
        return self._version

    def last_updated(self) -> Optional[datetime]:
        """Fetch the timestamp of the last cache reload."""
        return self._last_updated

    def set_policy(self, version: int, rules_payload: dict) -> None:
        """Update the cache in-place with a new policy."""
        self._active_policy = rules_payload
        self._version = version
        self._last_updated = datetime.now(tz=timezone.utc)
        self._reload_count += 1
        log.info(
            "PolicyCache: Loaded policy version %s (Reload count: %d)",
            version,
            self._reload_count,
        )

    def clear(self) -> None:
        """Clear cache (mostly for tests)."""
        self._active_policy = None
        self._version = None
        self._last_updated = None
        self._reload_count = 0
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> dict:
        """Return cache access statistics."""
        return {
            "version": self._version,
            "last_updated": self._last_updated.isoformat() if self._last_updated else None,
            "reload_count": self._reload_count,
            "hits": self._hits,
            "misses": self._misses,
        }
