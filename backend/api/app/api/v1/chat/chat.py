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
from core.models.model_registry import get_model_for
from core.models.agent_prompts import get_prompt_for
from core.config import cfg
from core.state import GraphState

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from functools import lru_cache

# ── Logger ────────────────────────────────────────────────────────────────────
log = logging.getLogger(__name__)

# ── Router ────────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/chat", tags=["chat"])


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

async def _run_graph(query: str) -> GraphState:
    """
    Run the synchronous LangGraph in a thread-pool.
    graph.invoke() is blocking — asyncio.to_thread() prevents event-loop stall.
    """
    return await asyncio.to_thread(graph.invoke, {"query": query})


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
) -> AsyncIterator[str]:
    """
    Core SSE generator.
    Yields SSE-formatted strings: start → metadata → token × N → done | error
    """
    model_name = model_override or get_model_for(intent.query_type)
    system_prompt = get_prompt_for(intent.query_type)
    llm = _get_llm(model_name)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query),
    ]

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
    try:
        async for chunk in llm.astream(messages):
            token: str = chunk.content
            if token:
                yield _sse_line(StreamChunk(
                    event="token",
                    data=token,
                    conversation_id=conversation_id,
                ))

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
async def chat(req: ChatRequest) -> ChatResponse:
    """
    Non-streaming chat endpoint.

    Flow:
      1. Run LangGraph (orchestrator → intent_agent → router) in thread-pool.
      2. Extract IntentResult from state.
      3. Call ChatGroq.ainvoke() with the right model + system prompt.
      4. Return structured ChatResponse.
    """
    log.info(
        "POST /chat | conversation_id=%s | user_id=%s",
        req.conversation_id, req.user_id,
    )

    t0 = time.monotonic()

    # ── Step 1: classify intent via graph ─────────────────────────────────────
    try:
        state: GraphState = await _run_graph(req.message)
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

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=req.message),
    ]

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

    return ChatResponse(
        conversation_id=req.conversation_id,
        user_id=req.user_id,
        response=response_text,
        routed_to=routed_to,
        intent=IntentMeta(**intent.model_dump()),
        latency_ms=latency_ms,
    )


@router.post("/stream")
async def chat_stream(req: ChatRequest, request: Request) -> StreamingResponse:
    """
    SSE streaming endpoint — ChatGPT-style token-by-token response.

    Flow:
      1. Run LangGraph in thread-pool to get IntentResult.
      2. Open ChatGroq.astream() with correct model + system prompt.
      3. Yield SSE frames: start → metadata → token × N → done | error.

    SSE event types:
      event:start    — stream opened
      event:metadata — intent classification + routing info (JSON)
      event:token    — one text chunk
      event:error    — error message string
      event:done     — stream complete
    """
    log.info(
        "POST /chat/stream | conversation_id=%s | user_id=%s",
        req.conversation_id, req.user_id,
    )

    # ── Step 1: classify intent ───────────────────────────────────────────────
    try:
        state: GraphState = await _run_graph(req.message)
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