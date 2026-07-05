from __future__ import annotations

import asyncio
import logging
import os

import redis.asyncio as aioredis

from app.db.session import AsyncSessionLocal
from core.agents.policy.cache import PolicyCache
from core.agents.policy.repository import PolicyRepository

log = logging.getLogger(__name__)

REDIS_CHANNEL = "policy.updated"
_POLL_INTERVAL = 0.1   # seconds between get_message() calls
_RECONNECT_DELAY = 5   # seconds before reconnect after error


async def reload_active_policy(session_factory=None) -> None:
    """Fetch the active policy from PostgreSQL and update the in-process cache."""
    if session_factory is None:
        session_factory = AsyncSessionLocal
    try:
        async with session_factory() as db:
            active_policy = await PolicyRepository.get_active_policy(db)
            if active_policy:
                PolicyCache().set_policy(
                    version=active_policy.version,
                    rules_payload=active_policy.rules_payload,
                )
                log.info(
                    "reload_active_policy: Loaded policy version %d.",
                    active_policy.version,
                )
            else:
                log.warning("reload_active_policy: No active policy found in DB.")
    except Exception as exc:
        log.error("reload_active_policy: Failed: %s", exc)


async def start_policy_subscriber(session_factory=None) -> None:
    """Redis Pub/Sub subscriber — listens on 'policy.updated'.

    Uses get_message() polling instead of blocking async-for listen() to
    stay compatible with the Windows asyncio ProactorEventLoop which stalls
    on long-lived socket reads without an explicit timeout.
    """
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    log.info("start_policy_subscriber: starting, channel=%s", REDIS_CHANNEL)

    while True:
        client: aioredis.Redis | None = None
        try:
            client = aioredis.from_url(
                redis_url,
                decode_responses=True,
                socket_timeout=3,
                socket_connect_timeout=3,
            )
            # Verify connection before entering the poll loop
            await client.ping()

            async with client.pubsub() as pubsub:
                await pubsub.subscribe(REDIS_CHANNEL)
                log.info(
                    "start_policy_subscriber: subscribed to '%s'.", REDIS_CHANNEL
                )

                # Poll loop — never blocks; yields control every _POLL_INTERVAL
                while True:
                    try:
                        message = await pubsub.get_message(
                            ignore_subscribe_messages=True,
                            timeout=_POLL_INTERVAL,
                        )
                    except asyncio.CancelledError:
                        raise
                    except Exception as read_err:
                        log.warning(
                            "start_policy_subscriber: read error: %s — reconnecting.",
                            read_err,
                        )
                        break  # outer while reconnects

                    if message and message.get("type") == "message":
                        data = message.get("data", "")
                        log.info(
                            "start_policy_subscriber: policy update received: %s", data
                        )
                        try:
                            await reload_active_policy(session_factory=session_factory)
                        except Exception as reload_err:
                            log.error(
                                "start_policy_subscriber: reload failed: %s", reload_err
                            )

                    # Yield control so other coroutines can run
                    await asyncio.sleep(_POLL_INTERVAL)

        except asyncio.CancelledError:
            log.info("start_policy_subscriber: cancelled.")
            break

        except Exception as exc:
            log.error(
                "start_policy_subscriber: connection error, retrying in %ds — %s",
                _RECONNECT_DELAY, exc,
            )
            await asyncio.sleep(_RECONNECT_DELAY)

        finally:
            if client:
                try:
                    await client.aclose()
                except Exception:
                    pass
