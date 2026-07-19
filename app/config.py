"""Central configuration, read once from the environment.

Everything that changes between "my laptop" and "Railway" lives here, so the rest
of the code never touches os.environ directly. That is the whole trick to a build
that runs the same locally and in the cloud.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

# Load a local .env when present. On Railway there is no file — the platform injects
# the same variables as real environment variables, so this is a no-op there.
# override=True so a stale empty shell var doesn't shadow .env locally. On Railway
# the file is absent, so this is still a no-op and the platform vars win.
load_dotenv(ROOT / ".env", override=True)
DATA_DIR = ROOT / "data"
WEB_DIR = ROOT / "web"
INDEX_PATH = DATA_DIR / "index.npz"

# --- Model choices -----------------------------------------------------------
# One chat model to answer, one embedding model to turn text into vectors.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
CHAT_MODEL = os.environ.get("CHAT_MODEL", "gpt-4o-mini")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "text-embedding-3-small")

# --- RAG knobs ---------------------------------------------------------------
# How big each chunk is (characters), how much neighbouring chunks overlap, and
# how many chunks we retrieve per question. These three numbers are most of RAG.
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "900"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "150"))
TOP_K = int(os.environ.get("TOP_K", "4"))

# Below this cosine similarity we treat retrieval as "found nothing relevant" and
# tell the model to refuse rather than invent an answer.
MIN_SCORE = float(os.environ.get("MIN_SCORE", "0.22"))

COMPANY_NAME = os.environ.get("COMPANY_NAME", "Northwind Robotics")
