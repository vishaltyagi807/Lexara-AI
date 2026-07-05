"""
chat.py — FastAPI chat router.

Integration map (read from codebase):
  graph.invoke({"query": str})  →  GraphState
    GraphState.intent           →  IntentResult  (query_type, complexity, cost …)
    GraphState.routed_to        →  str           (agent label)
    GraphState.agent_response   →  str           (stub — routing label only)
    GraphState.error            →  str | None

  response_agent.stream_response(query, intent) → str
    • picks model  via model_registry.get_model_for(query_type)
    • picks prompt via agent_prompts.get_prompt_for(query_type)
    • calls ChatGroq.stream() — sync generator, prints to stdout
    ⚠ stream_response() is sync + prints to stdout — not SSE-compatible.
      For /chat/stream we call ChatGroq.astream() directly, mirroring
      response_agent internals without the print() side-effects.

Assumptions:
  • graph (compiled LangGraph) is synchronous (invoke / no ainvoke yet).
    We run it in a thread-pool via asyncio.to_thread() to keep FastAPI async.
  • ChatGroq supports .astream() — confirmed by langchain-groq >= 0.1.
  • GROQ_API_KEY is present in env (loaded by core.config via dotenv).
  • This file lives at backend/api/app/api/v1/chat/chat.py.
    core/ must be on sys.path (handled by the app entrypoint / PYTHONPATH).
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from typing import AsyncIterator, Optional
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# ── Core layer imports (no business logic duplicated here) ────────────────────
from core.graph import graph                               # compiled LangGraph
from core.models.intent import IntentResult
from core.registry.model_registry import get_model_for
from core.prompts.response import get_prompt_for
from core.config import cfg
from core.graph.state import GraphState
from core.conversation.service import ConversationService
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, SystemMessage as LangChainSystemMessage
from functools import lru_cache

# ── Logger ────────────────────────────────────────────────────────────────────
log = logging.getLogger(__name__)

# ── Router ────────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/chat", tags=["chat"])

_conv_service = ConversationService()


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic schemas
# ─────────────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=32_000)
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    model: Optional[str] = None          # override model; None = use registry
    metadata: Optional[dict] = None


class IntentMeta(BaseModel):
    query_type: str
    complexity_score: int
    confidence: float
    execution_cost: str
    requires_tools: bool
    recommended_agent: str
    reasoning: str


class ChatResponse(BaseModel):
    conversation_id: str
    user_id: Optional[str]
    response: str
    routed_to: str
    intent: IntentMeta
    latency_ms: int


class StreamChunk(BaseModel):
    event: str          # start | metadata | token | error | done
    data: str           # token text, JSON metadata, error message, or ""
    conversation_id: str


# ─────────────────────────────────────────────────────────────────────────────
# Dependency injection
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=16)
def _get_llm(model_name: str) -> ChatGroq:
    """Cached LLM instance — one per model string."""
    return ChatGroq(
        model=model_name,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
    )


def get_groq_llm(request: ChatRequest = Depends()) -> ChatGroq:
    """Inject the correct LLM based on request.model or intent registry."""
    model_name = request.model or get_model_for("general_qa")
    return _get_llm(model_name)


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

async def _run_graph(query: str, chat_history: list[Any] | None = None, summary: str | None = None) -> GraphState:
    """
    Run the synchronous LangGraph in a thread-pool.
    graph.invoke() is blocking — asyncio.to_thread() prevents event-loop stall.
    """
    return await asyncio.to_thread(
        graph.invoke,
        {
            "query": query,
            "chat_history": chat_history,
            "summary": summary,
        }
    )


def _extract_intent(state: GraphState) -> IntentResult:
    intent = state.get("intent")
    if intent is None:
        raise HTTPException(status_code=500, detail="Intent classification returned None.")
    return intent


def _sse_line(chunk: StreamChunk) -> str:
    """Format a single SSE frame.

    The SSE spec forbids literal newlines inside a data: field.
    We encode non-scalar data (or data with embedded newlines) as JSON
    so every event is guaranteed to be a single-line data: value.
    """
    # Safely encode the data value; preserves all unicode & newlines.
    safe_data = json.dumps(chunk.data)
    return f"event:{chunk.event}\ndata:{safe_data}\n\n"


async def _stream_tokens(
    query: str,
    intent: IntentResult,
    conversation_id: str,
    model_override: Optional[str],
    db: AsyncSession,
    messages_history: list[Any],
    summary: Optional[str],
) -> AsyncIterator[str]:
    """
    Core SSE generator.
    Yields SSE-formatted strings: start → metadata → token × N → done | error
    """
    model_name = model_override or get_model_for(intent.query_type)
    system_prompt = get_prompt_for(intent.query_type)
    llm = _get_llm(model_name)

    # Hydrate messages with history + summary
    messages = [SystemMessage(content=system_prompt)]
    if summary:
        messages.append(LangChainSystemMessage(content=f"Summary of previous conversation: {summary}"))
    messages.extend(messages_history)
    messages.append(HumanMessage(content=query))

    # ── event: start ──────────────────────────────────────────────────────────
    yield _sse_line(StreamChunk(
        event="start",
        data="",
        conversation_id=conversation_id,
    ))

    # ── event: metadata ───────────────────────────────────────────────────────
    yield _sse_line(StreamChunk(
        event="metadata",
        data=json.dumps({
            "query_type":       intent.query_type,
            "complexity_score": intent.complexity_score,
            "execution_cost":   intent.execution_cost,
            "routed_to":        intent.recommended_agent,
            "model":            model_name,
        }),
        conversation_id=conversation_id,
    ))

    # ── event: token × N ─────────────────────────────────────────────────────
    full_response = ""
    t_start = time.monotonic()
    try:
        async for chunk in llm.astream(messages):
            token: str = chunk.content
            if token:
                full_response += token
                yield _sse_line(StreamChunk(
                    event="token",
                    data=token,
                    conversation_id=conversation_id,
                ))

        # Successfully streamed the entire response: persist in PostgreSQL
        latency_ms = int((time.monotonic() - t_start) * 1000)
        prompt_tokens = len(query.split())  # simple fallback estimation
        completion_tokens = len(full_response.split())

        interaction_metadata = {
            "provider": "groq",
            "model": model_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "latency_ms": latency_ms,
            "finish_reason": "stop",
        }

        await _conv_service.save_interaction(
            db,
            conversation_id,
            user_content=query,
            assistant_content=full_response,
            metadata=interaction_metadata,
        )

    except asyncio.CancelledError:
        log.warning("Stream cancelled | conversation_id=%s", conversation_id)
        yield _sse_line(StreamChunk(
            event="error",
            data="Stream cancelled by client.",
            conversation_id=conversation_id,
        ))
        return

    except Exception as exc:
        log.error("Streaming error | conversation_id=%s | error=%s", conversation_id, exc)
        yield _sse_line(StreamChunk(
            event="error",
            data="An error occurred during streaming.",
            conversation_id=conversation_id,
        ))
        return

    # ── event: done ───────────────────────────────────────────────────────────
    yield _sse_line(StreamChunk(
        event="done",
        data="",
        conversation_id=conversation_id,
    ))


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/health")
async def health() -> dict:
    """Liveness probe."""
    return {"status": "ok", "service": "chat"}


@router.post("/", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Non-streaming chat endpoint.

    Flow:
      1. Load conversation history and summary from DB/Cache.
      2. Run LangGraph (orchestrator → intent_agent → policy_agent → router) in thread-pool.
      3. Extract IntentResult from state.
      4. Call ChatGroq.ainvoke() with system prompt + summary + history + query.
      5. Save interaction atomically to DB and invalidate cache.
      6. Return structured ChatResponse.
    """
    log.info(
        "POST /chat | conversation_id=%s | user_id=%s",
        req.conversation_id, req.user_id,
    )

    t0 = time.monotonic()

    # Load history & summary from ConversationService
    messages_history, summary = await _conv_service.load_conversation_history(
        db, req.conversation_id, req.user_id
    )

    # ── Step 1: classify intent via graph ─────────────────────────────────────
    try:
        state: GraphState = await _run_graph(req.message, chat_history=messages_history, summary=summary)
    except Exception as exc:
        log.error("Graph execution failed | conversation_id=%s | error=%s", req.conversation_id, exc)
        raise HTTPException(status_code=500, detail="Graph execution failed.")

    intent = _extract_intent(state)
    routed_to = state.get("routed_to", intent.recommended_agent)

    log.info(
        "Graph complete | conversation_id=%s | query_type=%s | routed_to=%s",
        req.conversation_id, intent.query_type, routed_to,
    )

    # ── Step 2: generate response via LLM ────────────────────────────────────
    model_name = req.model or get_model_for(intent.query_type)
    system_prompt = get_prompt_for(intent.query_type)
    llm = _get_llm(model_name)

    log.info(
        "LLM invoke | conversation_id=%s | model=%s",
        req.conversation_id, model_name,
    )

    messages = [SystemMessage(content=system_prompt)]
    if summary:
        messages.append(LangChainSystemMessage(content=f"Summary of previous conversation: {summary}"))
    messages.extend(messages_history)
    messages.append(HumanMessage(content=req.message))

    try:
        ai_msg = await llm.ainvoke(messages)
        response_text: str = ai_msg.content
    except Exception as exc:
        log.error("LLM invoke failed | conversation_id=%s | error=%s", req.conversation_id, exc)
        raise HTTPException(status_code=502, detail="LLM response generation failed.")

    latency_ms = int((time.monotonic() - t0) * 1000)
    log.info(
        "Request complete | conversation_id=%s | latency_ms=%d",
        req.conversation_id, latency_ms,
    )

    # Save interaction atomically to DB and invalidate cache
    prompt_tokens = getattr(ai_msg, "response_metadata", {}).get("token_usage", {}).get("prompt_tokens")
    completion_tokens = getattr(ai_msg, "response_metadata", {}).get("token_usage", {}).get("completion_tokens")
    total_tokens = getattr(ai_msg, "response_metadata", {}).get("token_usage", {}).get("total_tokens")
    finish_reason = getattr(ai_msg, "response_metadata", {}).get("finish_reason")

    interaction_metadata = {
        "provider": "groq",
        "model": model_name,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "latency_ms": latency_ms,
        "finish_reason": finish_reason,
    }

    await _conv_service.save_interaction(
        db,
        req.conversation_id,
        user_content=req.message,
        assistant_content=response_text,
        metadata=interaction_metadata,
    )

    return ChatResponse(
        conversation_id=req.conversation_id,
        user_id=req.user_id,
        response=response_text,
        routed_to=routed_to,
        intent=IntentMeta(**intent.model_dump()),
        latency_ms=latency_ms,
    )


@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """
    SSE streaming endpoint — ChatGPT-style token-by-token response.

    Flow:
      1. Load conversation history and summary.
      2. Run LangGraph in thread-pool to get IntentResult.
      3. Open ChatGroq.astream() with correct model + system prompt + history.
      4. Yield SSE frames: start → metadata → token × N → done | error.
    """
    log.info(
        "POST /chat/stream | conversation_id=%s | user_id=%s",
        req.conversation_id, req.user_id,
    )

    # Load history & summary from ConversationService
    messages_history, summary = await _conv_service.load_conversation_history(
        db, req.conversation_id, req.user_id
    )

    # ── Step 1: classify intent ───────────────────────────────────────────────
    try:
        state: GraphState = await _run_graph(req.message, chat_history=messages_history, summary=summary)
    except Exception as exc:
        log.error(
            "Graph execution failed | conversation_id=%s | error=%s",
            req.conversation_id, exc,
        )
        raise HTTPException(status_code=500, detail="Graph execution failed.")

    intent = _extract_intent(state)

    log.info(
        "Streaming | conversation_id=%s | query_type=%s | model=%s",
        req.conversation_id,
        intent.query_type,
        req.model or get_model_for(intent.query_type),
    )

    # ── Step 2: stream tokens ─────────────────────────────────────────────────
    async def event_generator() -> AsyncIterator[str]:
        async for frame in _stream_tokens(
            query=req.message,
            intent=intent,
            conversation_id=req.conversation_id,
            model_override=req.model,
            db=db,
            messages_history=messages_history,
            summary=summary,
        ):
            # Stop if client disconnected
            if await request.is_disconnected():
                log.info("Client disconnected | conversation_id=%s", req.conversation_id)
                return
            yield frame

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",        # disable nginx buffering
            "Connection": "keep-alive",
        },
    )


@router.get("/history")
async def get_conversations_history(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
    include_archived: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve paginated conversation list for a user."""
    convs = await _conv_service.repo.get_user_conversations(
        db, user_id=user_id, limit=limit, offset=offset, search=search, include_archived=include_archived
    )
    return [
        {
            "id": str(c.id),
            "title": c.title,
            "summary": c.summary,
            "is_archived": c.is_archived,
            "is_pinned": c.is_pinned,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat(),
        }
        for c in convs
    ]


@router.get("/{conversation_id}")
async def get_conversation_details(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve full messages list for a conversation."""
    conv = await _conv_service.repo.get_or_create_conversation(db, conversation_id)
    messages = await _conv_service.repo.get_messages(db, conversation_id, limit=100)
    return {
        "id": str(conv.id),
        "title": conv.title,
        "summary": conv.summary,
        "is_archived": conv.is_archived,
        "is_pinned": conv.is_pinned,
        "messages": [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat(),
                "provider": m.provider,
                "model": m.model,
            }
            for m in messages
        ]
    }


@router.put("/{conversation_id}")
async def rename_conversation(
    conversation_id: str,
    title: str,
    db: AsyncSession = Depends(get_db),
):
    """Rename conversation title manually."""
    await _conv_service.repo.rename_conversation(db, conversation_id, title)
    await _conv_service.cache.invalidate_cache(conversation_id)
    return {"status": "ok", "message": "Conversation renamed successfully."}


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Soft delete conversation."""
    await _conv_service.repo.soft_delete_conversation(db, conversation_id, is_deleted=True)
    await _conv_service.cache.invalidate_cache(conversation_id)
    return {"status": "ok", "message": "Conversation soft deleted."}


@router.post("/{conversation_id}/archive")
async def archive_conversation(
    conversation_id: str,
    is_archived: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Archive conversation."""
    await _conv_service.repo.archive_conversation(db, conversation_id, is_archived=is_archived)
    await _conv_service.cache.invalidate_cache(conversation_id)
    return {"status": "ok", "message": "Conversation archived."}


@router.post("/{conversation_id}/restore")
async def restore_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Restore soft deleted/archived conversation."""
    await _conv_service.repo.soft_delete_conversation(db, conversation_id, is_deleted=False)
    await _conv_service.repo.archive_conversation(db, conversation_id, is_archived=False)
    await _conv_service.cache.invalidate_cache(conversation_id)
    return {"status": "ok", "message": "Conversation restored."}


@router.get("/{conversation_id}/export")
async def export_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Export conversation history as JSON."""
    from datetime import datetime, timezone
    conv = await _conv_service.repo.get_or_create_conversation(db, conversation_id)
    messages = await _conv_service.repo.get_messages(db, conversation_id, limit=200)
    return {
        "export_timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "conversation_id": str(conv.id),
        "title": conv.title,
        "summary": conv.summary,
        "history": [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.created_at.isoformat(),
                "metadata": m.metadata_payload,
            }
            for m in messages
        ]
    }