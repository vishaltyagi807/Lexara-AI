from __future__ import annotations

from typing import Any
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from core.conversation.models import Message


def db_message_to_langchain(msg: Message) -> BaseMessage:
    """Convert a database Message model instance to a LangChain BaseMessage subclass."""
    content = msg.content
    role = msg.role.lower()
    
    # Store token usage, provider, latency, etc. in message metadata
    additional_kwargs = {}
    if msg.tool_calls:
        additional_kwargs["tool_calls"] = msg.tool_calls
        
    response_metadata = {
        "provider": msg.provider,
        "model": msg.model,
        "prompt_tokens": msg.prompt_tokens,
        "completion_tokens": msg.completion_tokens,
        "total_tokens": msg.total_tokens,
        "latency_ms": msg.latency_ms,
        "finish_reason": msg.finish_reason,
    }

    if role == "user":
        return HumanMessage(content=content, additional_kwargs=additional_kwargs, response_metadata=response_metadata)
    elif role in ("assistant", "ai"):
        return AIMessage(content=content, additional_kwargs=additional_kwargs, response_metadata=response_metadata)
    elif role == "system":
        return SystemMessage(content=content, additional_kwargs=additional_kwargs, response_metadata=response_metadata)
    else:
        # Fallback to general base message subclass or HumanMessage
        return HumanMessage(content=content, additional_kwargs=additional_kwargs, response_metadata=response_metadata)


def langchain_to_db_payload(msg: BaseMessage, conversation_id: Any) -> dict[str, Any]:
    """Convert a LangChain message object to a dict database payload for saving."""
    role = "user"
    if isinstance(msg, AIMessage):
        role = "assistant"
    elif isinstance(msg, SystemMessage):
        role = "system"
        
    content = msg.content
    tool_calls = msg.additional_kwargs.get("tool_calls")
    
    response_metadata = getattr(msg, "response_metadata", {}) or {}
    
    return {
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "tool_calls": tool_calls,
        "provider": response_metadata.get("provider"),
        "model": response_metadata.get("model"),
        "prompt_tokens": response_metadata.get("prompt_tokens"),
        "completion_tokens": response_metadata.get("completion_tokens"),
        "total_tokens": response_metadata.get("total_tokens"),
        "latency_ms": response_metadata.get("latency_ms"),
        "finish_reason": response_metadata.get("finish_reason"),
    }
