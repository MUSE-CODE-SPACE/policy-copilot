"""Ingestion: PDF -> text -> chunks -> embeddings -> saved index.

Run this once whenever the policy documents change:

    python -m app.rag.ingest

It reads every PDF in data/, splits the text into overlapping chunks, embeds them,
and writes data/index.npz. The running server never re-embeds documents — it just
loads that file at startup.
"""
from __future__ import annotations

import sys
from pathlib import Path

from pypdf import PdfReader

from .. import config, llm
from .store import VectorStore


def pdf_to_text(path: Path) -> str:
    """Extract text from every page and join it into one string."""
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Split text into ~`size`-char windows that overlap by `overlap` chars.

    Overlap matters: a sentence that straddles a chunk boundary would otherwise be
    cut in half and become unfindable. The overlap keeps that context in both chunks.
    We break on paragraph/whitespace where we can so chunks don't slice mid-word.
    """
    text = " ".join(text.split())  # normalise whitespace
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        # try to end on a sentence/space boundary near the target end
        if end < len(text):
            window = text.rfind(" ", start + size - overlap, end)
            if window != -1:
                end = window
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = end - overlap
    return [c for c in chunks if c]


def build_index(data_dir: Path = config.DATA_DIR) -> VectorStore:
    pdfs = sorted(data_dir.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs found in {data_dir}. Add a policy PDF and retry.")

    all_texts: list[str] = []
    all_sources: list[str] = []
    for pdf in pdfs:
        raw = pdf_to_text(pdf)
        chunks = chunk_text(raw, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        print(f"  {pdf.name}: {len(chunks)} chunks")
        all_texts.extend(chunks)
        all_sources.extend([pdf.name] * len(chunks))

    print(f"Embedding {len(all_texts)} chunks with {config.EMBED_MODEL} ...")
    # Embed in batches so a big handbook doesn't hit request-size limits.
    vecs = []
    for i in range(0, len(all_texts), 64):
        batch = all_texts[i : i + 64]
        vecs.append(llm.embed(batch))
    import numpy as np

    store = VectorStore(np.vstack(vecs), all_texts, all_sources)
    store.save(config.INDEX_PATH)
    print(f"Saved index: {config.INDEX_PATH} ({len(store)} vectors)")
    return store


if __name__ == "__main__":
    build_index()
    sys.exit(0)
