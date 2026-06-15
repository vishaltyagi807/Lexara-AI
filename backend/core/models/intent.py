"""Pydantic models — single schema file for the intent layer."""
from typing import Literal
from pydantic import BaseModel, Field


QueryType = Literal[
    "reasoning", "coding", "mathematics", "data_analysis",
    "research", "general_qa", "conversation", "summarization",
    "extraction", "tool_execution", "unknown",
]

ExecutionCost = Literal["low", "medium", "high"]


class IntentResult(BaseModel):
    query_type: QueryType
    complexity_score: int = Field(..., ge=1, le=10)
    confidence: float = Field(..., ge=0.0, le=1.0)
    execution_cost: ExecutionCost
    requires_tools: bool
    recommended_agent: str
    reasoning: str