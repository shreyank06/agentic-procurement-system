"""
Core backend module - Catalog, embeddings, and procurement logic.

Exports:
  - Catalog: Main catalog class
  - EmbeddingManager: Vector embeddings management
  - LLMAdapter: LLM abstraction interface
  - Procurement functions: plan_procurement, negotiate_procurement
"""

from backend.core.catalog import Catalog
from backend.core.embeddings import EmbeddingManager
from backend.core.llm_adapter import LLMAdapter, MockLLM, OpenAILLM, select_llm_provider
from backend.core.procurement import plan_procurement, negotiate_procurement, compute_score

__all__ = [
    "Catalog",
    "EmbeddingManager",
    "LLMAdapter",
    "MockLLM",
    "OpenAILLM",
    "select_llm_provider",
    "plan_procurement",
    "negotiate_procurement",
    "compute_score"
]
