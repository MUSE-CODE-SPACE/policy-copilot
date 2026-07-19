"""Turning retrieved chunks into the messages we send the model.

This is the "A" (augmented) in RAG: we don't ask the model what it *thinks* the
policy is — we paste the relevant handbook passages into the prompt and instruct it
to answer *only* from them, with citations. That is what turns a chatty model into a
grounded assistant that won't invent a vacation policy.
"""
from __future__ import annotations

from .config import COMPANY_NAME
from .rag.store import Hit

SYSTEM = f"""You are Policy Copilot, the internal assistant for {COMPANY_NAME}.
You answer employee questions about company policy using ONLY the excerpts from the
official handbook provided in each turn.

Rules:
- Answer strictly from the provided CONTEXT. Do not use outside knowledge.
- If the context does not contain the answer, say so plainly and suggest who to ask
  (e.g. People Ops). Never guess a number, date, or entitlement.
- Be concise and specific. Quote the exact figure or rule when the context gives one.
- Cite the source file in brackets like [handbook.pdf] after the relevant sentence.
- Keep a helpful, professional tone.
"""


def build_context(hits: list[Hit]) -> str:
    if not hits:
        return "(no relevant handbook passages were found for this question)"
    blocks = []
    for h in hits:
        # Label each passage with its filename (not a number) so the model copies the
        # filename into its citation, e.g. [handbook.pdf].
        blocks.append(f"--- from {h.source} ---\n{h.text}")
    return "\n\n".join(blocks)


def build_messages(question: str, hits: list[Hit], history: list[dict] | None = None) -> list[dict]:
    context = build_context(hits)
    messages: list[dict] = [{"role": "system", "content": SYSTEM}]
    if history:
        # keep the last few turns for follow-up questions ("what about part-timers?")
        messages.extend(history[-6:])
    messages.append(
        {
            "role": "user",
            "content": f"CONTEXT (official handbook excerpts):\n{context}\n\n"
            f"QUESTION: {question}",
        }
    )
    return messages
