"""model_registry.py — backward-compatibility shim.

MODEL_REGISTRY and get_model_for() have moved to core/registry/model_registry.py.
This file re-exports them so any existing code using:
    from core.models.model_registry import get_model_for
continues to work without changes.
"""
from core.registry.model_registry import MODEL_REGISTRY, get_model_for  # noqa: F401

__all__ = ["MODEL_REGISTRY", "get_model_for"]