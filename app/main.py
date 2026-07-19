"""The web server: serves the chat UI and answers questions over a streaming API.

One FastAPI app does everything — it hosts the static frontend AND exposes the RAG
endpoint — so the whole product deploys to Railway as a single service.
"""
from __future__ import annotations

import json

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import config, prompts
from .llm import chat_stream
from .rag.retrieve import get_store, retrieve

app = FastAPI(title="Policy Copilot", version="1.0")


@app.get("/api/health")
def health() -> JSONResponse:
    """Cheap liveness + index-size check (used by Railway and by us during the demo)."""
    try:
        n = len(get_store())
    except Exception as e:  # index missing etc.
        return JSONResponse({"ok": False, "error": str(e)}, status_code=503)
    return JSONResponse(
        {"ok": True, "company": config.COMPANY_NAME, "chunks": n, "model": config.CHAT_MODEL}
    )


@app.post("/api/chat")
async def chat(request: Request) -> StreamingResponse:
    """Server-Sent Events stream: first the sources we retrieved, then answer tokens.

    Payload: { "question": str, "history": [{role, content}, ...] }
    """
    body = await request.json()
    question = (body.get("question") or "").strip()
    history = body.get("history") or []

    def sse(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    def generate():
        if not question:
            yield sse("error", {"message": "Empty question."})
            return

        # 1) RETRIEVE — find the handbook passages that matter for this question.
        hits = retrieve(question)
        yield sse(
            "sources",
            {"sources": [{"source": h.source, "score": round(h.score, 3)} for h in hits]},
        )

        # 2) AUGMENT — paste those passages into a grounded prompt.
        messages = prompts.build_messages(question, hits, history)

        # 3) GENERATE — stream the grounded answer back token by token.
        try:
            for token in chat_stream(messages):
                yield sse("token", {"text": token})
        except Exception as e:
            yield sse("error", {"message": str(e)})
            return
        yield sse("done", {})

    return StreamingResponse(generate(), media_type="text/event-stream")


# Serve the static frontend. Mounted last so /api/* routes win.
@app.get("/")
def index() -> FileResponse:
    return FileResponse(config.WEB_DIR / "index.html")


app.mount("/", StaticFiles(directory=str(config.WEB_DIR)), name="web")
