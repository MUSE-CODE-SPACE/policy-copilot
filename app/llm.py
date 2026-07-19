"""The two calls we make to the model provider: embed text, and stream a chat reply.

This is the *only* file that imports the OpenAI SDK. Every other module talks to
"the model" through these two functions, so swapping providers later is a one-file
change.
"""
from __future__ import annotations

from typing import Iterable, Iterator

import numpy as np
from openai import OpenAI

from . import config

_client: OpenAI | None = None


def client() -> OpenAI:
    """Lazily build the SDK client so importing this module never needs a key."""
    global _client
    if _client is None:
        if not config.OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Put it in .env locally, or in Railway's "
                "Variables tab in production."
            )
        _client = OpenAI(api_key=config.OPENAI_API_KEY)
    return _client


def embed(texts: list[str]) -> np.ndarray:
    """Turn a list of strings into an (n, dim) float32 matrix of unit vectors.

    We L2-normalise here so that later a plain dot product == cosine similarity.
    """
    resp = client().embeddings.create(model=config.EMBED_MODEL, input=texts)
    vecs = np.array([d.embedding for d in resp.data], dtype=np.float32)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vecs / norms


def embed_one(text: str) -> np.ndarray:
    """Embed a single string -> (dim,) unit vector."""
    return embed([text])[0]


def chat_stream(messages: list[dict]) -> Iterator[str]:
    """Stream the assistant reply token-by-token as plain text deltas."""
    stream = client().chat.completions.create(
        model=config.CHAT_MODEL,
        messages=messages,
        temperature=0.2,
        stream=True,
    )
    for event in stream:
        delta = event.choices[0].delta.content if event.choices else None
        if delta:
            yield delta
