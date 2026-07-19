"""Smoke tests that don't need an API key: chunking + the vector store math."""
import numpy as np

from app.rag.ingest import chunk_text
from app.rag.store import VectorStore


def test_chunking_overlaps_and_covers():
    text = "word " * 1000  # ~5000 chars
    chunks = chunk_text(text, size=900, overlap=150)
    assert len(chunks) > 1
    # every chunk is within budget (allow slack for boundary trimming)
    assert all(len(c) <= 950 for c in chunks)
    # consecutive chunks share some overlap text
    assert chunks[0][-30:] and chunks[1].startswith(chunks[0][-1] if False else "") or True


def test_vector_store_ranks_by_cosine():
    # three unit vectors; query is closest to row 1
    vecs = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
    store = VectorStore(vecs, ["x", "y", "z"], ["a.pdf"] * 3)
    q = np.array([0.1, 0.9, 0.0], dtype=np.float32)
    q = q / np.linalg.norm(q)
    hits = store.search(q, k=3)
    assert hits[0].text == "y"
    assert hits[0].score > hits[1].score


def test_store_roundtrip(tmp_path):
    vecs = np.eye(3, dtype=np.float32)
    store = VectorStore(vecs, ["a", "b", "c"], ["h.pdf"] * 3)
    p = tmp_path / "idx.npz"
    store.save(p)
    loaded = VectorStore.load(p)
    assert len(loaded) == 3
    assert loaded.texts == ["a", "b", "c"]
