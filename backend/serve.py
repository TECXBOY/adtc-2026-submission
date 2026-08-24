"""
Local inference server — POST /ask returns a streamed answer.

Architecture (per BOB_ADDENDUM_pre-step4.md):
  - This process owns the model and RAG pipeline entirely.
  - The UI (Step 5) is a pure HTTP client of this server.
  - No UI code is imported here; no model object is shared across processes.
  - Default binding: 127.0.0.1 (localhost only, per competition rules).
  - LAN mode: set server.lan_mode: true in config.yaml to bind to 0.0.0.0.
    MUST be false for the ADTC submission — see config.yaml comment.

Endpoints:
  POST /ask          — stream an answer (SSE)
  GET  /healthz      — liveness check
  GET  /corpus/stats — corpus metadata
"""

import asyncio
import json
import socket
import sys
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── Resolve project root (one level up from backend/) ──────────────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.retriever import TFIDFRetriever
from backend.prompt import build_prompt

# ── Config ──────────────────────────────────────────────────────────────────
cfg_path = ROOT / "config.yaml"
with open(cfg_path) as f:
    cfg = yaml.safe_load(f)

assert not cfg["server"].get("allow_network", True), (
    "config.yaml: server.allow_network must be false"
)

LAN_MODE      = cfg["server"].get("lan_mode", False)
HOST          = "0.0.0.0" if LAN_MODE else cfg["server"].get("host", "127.0.0.1")
PORT          = cfg["server"].get("port", 8000)
MODEL_PATH    = ROOT / cfg["model"]["gguf_path"]
N_CTX         = cfg["model"].get("context_window", 2048)
MAX_TOKENS    = cfg["inference"].get("max_new_tokens", 512)
TEMPERATURE   = cfg["inference"].get("temperature", 0.2)
TOP_K_RAG     = cfg["rag"].get("top_k", 3)
MAX_INPUT     = cfg["robustness"].get("max_input_chars", 4000)
REJECT_EMPTY  = cfg["robustness"].get("reject_empty_input", True)

# ── Load model (once at startup) ────────────────────────────────────────────
print(f"Loading model: {MODEL_PATH}", flush=True)
from llama_cpp import Llama

llm = Llama(
    model_path=str(MODEL_PATH),
    n_ctx=N_CTX,
    n_threads=4,
    n_gpu_layers=0,   # CPU-only — never assume GPU
    verbose=False,
)
print("Model loaded.", flush=True)

# ── Load retriever (once at startup) ────────────────────────────────────────
retriever = TFIDFRetriever(index_dir=str(ROOT / cfg["rag"]["vector_index_path"]))
print(f"Retriever ready: {len(retriever.records)} records", flush=True)

# ── Inference lock — queue concurrent requests rather than colliding ─────────
# llama.cpp is not re-entrant; a second call while one is in flight will
# corrupt state. The asyncio lock ensures requests are processed one at a time.
_inference_lock = asyncio.Lock()

# ── LAN startup banner ───────────────────────────────────────────────────────
def _local_ip() -> str:
    """Best-effort: get the machine's LAN IP (not loopback)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))   # doesn't actually send anything
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unknown"

if LAN_MODE:
    lan_ip = _local_ip()
    print("", flush=True)
    print("╔══════════════════════════════════════════════════╗", flush=True)
    print("║  LAN MODE ENABLED                                ║", flush=True)
    print(f"║  Reachable on your network at:                   ║", flush=True)
    print(f"║  http://{lan_ip}:{PORT:<5}                          ║", flush=True)
    print("║                                                  ║", flush=True)
    print("║  ⚠ Set lan_mode: false before ADTC submission  ║", flush=True)
    print("╚══════════════════════════════════════════════════╝", flush=True)
    print("", flush=True)
else:
    print(f"Server: http://127.0.0.1:{PORT} (localhost only)", flush=True)

# ── FastAPI app ─────────────────────────────────────────────────────────────
app = FastAPI(title="WASSCE/BECE Offline Tutor", version="0.1.0")

# CORS: in LAN mode allow any origin so phones/tablets on the network can reach
# the UI. In localhost mode, restrict to known local origins.
if LAN_MODE:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

# Serve the chat UI from /
FRONTEND_DIR = ROOT / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
def serve_ui():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


# ── Request/response schemas ─────────────────────────────────────────────────
class AskRequest(BaseModel):
    question: str


# ── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "model": cfg["model"]["active"],
        "lan_mode": LAN_MODE,
    }


@app.get("/corpus/stats")
def corpus_stats():
    subjects = {}
    for r in retriever.records:
        subjects[r["subject"]] = subjects.get(r["subject"], 0) + 1
    return {
        "total_records": len(retriever.records),
        "subjects": subjects,
        "source": "hand-curated",
    }


@app.post("/ask")
async def ask(req: AskRequest):
    question = req.question

    # ── Input validation (robustness) ───────────────────────────────────────
    if REJECT_EMPTY and not question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")
    if len(question) > MAX_INPUT:
        raise HTTPException(
            status_code=400,
            detail=f"Question exceeds maximum length ({MAX_INPUT} characters).",
        )

    # ── Retrieve + build prompt ─────────────────────────────────────────────
    retrieved = retriever.retrieve(question.strip(), top_k=TOP_K_RAG)
    messages  = build_prompt(question.strip(), retrieved)

    # ── Stream response as SSE ──────────────────────────────────────────────
    async def generate():
        # Opening SSE envelope — includes metadata for the UI
        meta = {
            "event": "meta",
            "response_type": "full_solution",
            "retrieved_ids": [r["id"] for r in retrieved],
        }
        yield f"data: {json.dumps(meta)}\n\n"

        # Acquire lock — queue concurrent requests rather than crashing
        async with _inference_lock:
            try:
                for chunk in llm.create_chat_completion(
                    messages=messages,
                    max_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE,
                    stream=True,
                ):
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield f"data: {json.dumps({'event': 'token', 'text': delta})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'event': 'error', 'detail': str(e)})}\n\n"
            finally:
                yield f"data: {json.dumps({'event': 'done'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
