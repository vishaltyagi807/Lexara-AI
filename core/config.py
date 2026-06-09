"""Centralized configuration — single source of truth."""
from dataclasses import dataclass, field
from dotenv import load_dotenv
load_dotenv()


@dataclass(frozen=True)
class Config:
    model_name: str = "llama-3.3-70b-versatile"
    temperature: float = 0.0
    max_tokens: int = 1024
    log_level: str = "INFO"

    # Maps intent → agent label (extend here to add new agents)
    routing_map: dict[str, str] = field(default_factory=lambda: {
        "coding":        "CodingAgent",
        "mathematics":   "MathAgent",
        "reasoning":     "ReasoningAgent",
        "research":      "ResearchAgent",
        "data_analysis": "DataAnalysisAgent",
        "summarization": "GeneralAgent",
        "extraction":    "GeneralAgent",
        "tool_execution":"GeneralAgent",
        "general_qa":    "GeneralAgent",
        "conversation":  "GeneralAgent",
        "unknown":       "GeneralAgent",
    })


cfg = Config()