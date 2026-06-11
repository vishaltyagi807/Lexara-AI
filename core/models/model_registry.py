"""Model registry — maps query_type → model string.

This is the ONLY file to edit when assigning different models to different tasks.
Adding a new task model = one line here, nothing else changes.
"""

# Default model used for all tasks right now
_DEFAULT = "openai/gpt-oss-120b"

# Future: assign specific models per task type for token efficiency
# e.g. "coding": "deepseek-r1-distill-llama-70b"  (better at code)
#      "mathematics": "deepseek-r1-distill-llama-70b"  (better at math)
#      "conversation": "llama-3.1-8b-instant"  (lightweight, fast)
MODEL_REGISTRY: dict[str, str] = {
    "coding":        _DEFAULT,
    "mathematics":   _DEFAULT,
    "reasoning":     _DEFAULT,
    "research":      _DEFAULT,
    "data_analysis": _DEFAULT,
    "summarization": _DEFAULT,
    "extraction":    _DEFAULT,
    "tool_execution":_DEFAULT,
    "general_qa":    _DEFAULT,
    "conversation":  _DEFAULT,
    "unknown":       _DEFAULT,
}


def get_model_for(query_type: str) -> str:
    """Return the model string for a given query type."""
    return MODEL_REGISTRY.get(query_type, _DEFAULT)