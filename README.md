# WASSCE/BECE Offline Math & Science Tutor

Offline, on-device tutoring assistant for West African secondary-school exam
prep (WASSCE / BECE). Runs entirely on-device with no cloud dependency —
built for the ADTC 2026 Laptop LLM Challenge, Math & Scientific Reasoning track.

## What it does
Solves and explains WASSCE/BECE-style math and science problems with
step-by-step reasoning, grounded via retrieval over a local corpus of real
past exam questions. No internet connection required at inference time.

## Target hardware
ADTC Standard Laptop profile: Intel Core i5 10th–12th gen / AMD Ryzen 5
3000–5000, 8GB RAM (7GB hard ceiling), integrated graphics only,
Ubuntu 22.04 LTS.

## Quickstart
```bash
git clone <this repo>
cd <this repo>
bash download_model.sh       # downloads the quantized GGUF model
pip install -r requirements.txt
python backend/serve.py      # starts local inference server
# open the UI at http://localhost:8000
```

No network access is required after `download_model.sh` completes.

## Architecture
```
Local Web UI (chat interface)
        │  HTTP, localhost only
Backend / Inference Server
        │  loads quantized GGUF model via llama.cpp
        │  RAG retrieval over local WASSCE/BECE corpus
        │  streams tokens back to UI
Local Data & Model Assets
        │  GGUF weights (downloaded, not committed)
        │  WASSCE/BECE corpus + local vector index
```

## Corpus
50 original questions written to match real WASSCE/BECE format, syllabus
topics, and difficulty levels — not sourced from actual past papers.
30 Mathematics + 20 Integrated Science, spanning BECE and WASSCE level.
Each record in `corpus/wassce_bece_questions.jsonl` carries
`"source": "hand-curated"` for provenance tracking.
See `DECISIONS.md` for the full corpus decision log.

## Report and benchmarks
See `REPORT.md` for the full technical writeup, design decisions, and
measured Sperf/Seff numbers from `adtc-profiler`.

## Project status
See `TASKS.md` for build sequence and progress. See `DECISIONS.md` for the
model/quantization/corpus decisions and reasoning behind them.

## LAN Classroom Mode (optional)

One laptop can serve the tutor to multiple student devices on the same WiFi
network — no internet required, everything stays local.

**To enable:**
1. In `config.yaml`, change `lan_mode: false` to `lan_mode: true`
2. Start the server with `--host 0.0.0.0`:
   ```bash
   .venv/bin/python3 -m uvicorn backend.serve:app --host 0.0.0.0 --port 8000
   ```
3. The terminal prints your laptop's LAN address, e.g. `http://192.168.1.42:8000`
4. Open that URL on any phone, tablet, or other laptop on the same network

**To disable:** set `lan_mode: false` in `config.yaml` and restart the server.

> **Competition rule:** `lan_mode` must be `false` for the ADTC evaluation.
> The default is `false` — only flip it for demos, then flip it back.

## License
TBD — confirm before submission; must permit competition use and
redistribution of model weights via `download_model.sh`.
