"""A tiny vector store, in plain NumPy.

A "vector database" sounds heavy, but at its core it is exactly this: a matrix of
embeddings, the original text for each row, and a function that finds the rows most
similar to a query vector. Seeing it in ~40 lines is the point — once you get this,
Pinecone / Chroma / pgvector are just this idea with persistence, filtering, and
scale bolted on.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class Hit:
    text: str
    source: str
    score: float


class VectorStore:
    def __init__(self, vectors: np.ndarray, texts: list[str], sources: list[str]):
        # vectors: (n, dim) unit vectors. texts/sources: length n, aligned by row.
        self.vectors = vectors.astype(np.float32)
        self.texts = texts
        self.sources = sources

    def __len__(self) -> int:
        return len(self.texts)

    def search(self, query_vec: np.ndarray, k: int) -> list[Hit]:
        """Cosine similarity == dot product, because everything is unit-normalised."""
        scores = self.vectors @ query_vec  # (n,)
        top = np.argsort(-scores)[:k]
        return [
            Hit(text=self.texts[i], source=self.sources[i], score=float(scores[i]))
            for i in top
        ]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path,
            vectors=self.vectors,
            texts=np.array(self.texts, dtype=object),
            sources=np.array(self.sources, dtype=object),
        )

    @classmethod
    def load(cls, path: Path) -> "VectorStore":
        data = np.load(path, allow_pickle=True)
        return cls(
            vectors=data["vectors"],
            texts=list(data["texts"]),
            sources=list(data["sources"]),
        )
