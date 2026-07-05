from __future__ import annotations

import json
from typing import Any
from pydantic import BaseModel


def to_jsonable(obj: Any) -> Any:
    """Recursively convert objects (including Pydantic models) to JSON-serializable types."""
    if obj is None:
        return None
    if isinstance(obj, BaseModel):
        return obj.model_dump(mode="json")
    if isinstance(obj, (dict, list, str, int, float, bool)):
        if isinstance(obj, dict):
            return {k: to_jsonable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [to_jsonable(v) for v in obj]
        return obj
    try:
        # Fallback to json serialization test
        json.dumps(obj)
        return obj
    except (TypeError, OverflowError):
        return str(obj)
