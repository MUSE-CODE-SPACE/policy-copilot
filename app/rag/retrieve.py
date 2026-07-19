"""Retrieval: given a user question, find the most relevant policy chunks.

This is the "R" in RAG. The index is loaded once and kept in memory; each query is
embedded and compared against every stored chunk. For a handbook-sized corpus that
brute-force scan is instant and needs no external database.
"""
from __future__ import annotations

from functools import lru_cache

from .. import config, llm
from .store import Hit, VectorStore


@lru_cache(maxsize=1)
def get_store() -> VectorStore:
    """Load the prebuilt index once and cache it for the process lifetime."""
    if not config.INDEX_PATH.exists():
        raise RuntimeError(
            f"No index at {config.INDEX_PATH}. Run `python -m app.rag.ingest` first."
        )
    return VectorStore.load(config.INDEX_PATH)


def retrieve(question: str, k: int | None = None) -> list[Hit]:
    """Return up to k chunks above the relevance floor, best first."""
    k = k or config.TOP_K
    store = get_store()
    query_vec = llm.embed_one(question)
    hits = store.search(query_vec, k)
    return [h for h in hits if h.score >= config.MIN_SCORE]
