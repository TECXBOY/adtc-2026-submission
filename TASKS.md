# Build Sequence — do not reorder

Each step must produce a runnable checkpoint with real output shown before
moving to the next. No speculative full-stack building.

## 1. Environment setup
- [x] Clone official ADTC 2026 submission template repo
- [x] Install `adtc-profiler`: `pip install "git+https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler.git"`
- [x] Confirm profiler runs against a placeholder/dummy model
- **Checkpoint:** profiler produces output on a dummy model ✅

## 2. Model selection and quantization test
- [x] Download 2–3 candidate small (1B–4B) instruct models in GGUF form
- [x] Load each via llama.cpp locally
- [x] Run raw WASSCE/BECE-style math questions, no RAG yet
- [x] Record answer quality, tokens/sec, peak RAM per candidate
- [x] Pick model empirically, log decision + numbers in `DECISIONS.md`
- **Checkpoint:** table of real numbers per candidate model ✅
  - SmolLM2-1.7B Q4_K_M: 5/5 correct · 2.5 t/s · 1346 MB ← **CHOSEN**
  - Gemma-2-2B Q4_K_M:   1/5 within timeout · 1.6 t/s · 1948 MB ← rejected

## 3. Corpus build
- [x] Confirm corpus sourcing/licensing — hand-curated original content, no license blocker
- [x] Compile WASSCE/BECE past-question corpus (50 questions → corpus/wassce_bece_questions.jsonl)
- [x] Build local TF-IDF index (corpus/index/) via build_index.py
- [x] Validate retrieval quality on test questions
- **Checkpoint:** retrieval returns relevant chunks for test queries ✅
  - "solve for x linear equation" → Q001 Linear Equations (0.278)
  - "area of a circle radius" → Q009 Mensuration Circle (0.449)
  - "Newton's law of motion" → Q036 Force and Motion (0.359)

## 4. RAG + inference pipeline
- [x] Wire retrieval into prompt construction (backend/retriever.py + backend/prompt.py)
- [x] Connect to chosen model (backend/serve.py — FastAPI + SSE, client-server architecture)
- [x] Confirm grounded answers — SSE stream live, correct corpus chunks retrieved
- [x] Input validation: empty input → 400, length cap enforced
- **Checkpoint:** side-by-side raw vs. RAG answers, RAG visibly better ✅
  - POST /ask → SSE stream with meta (retrieved_ids) + token events + done
  - Retrieved Q009 (circle area) correctly for circle question
  - GET /healthz and GET /corpus/stats working

## 5. Minimal UI
- [x] Build chat interface (frontend/index.html — SSE client, streaming tokens)
- [x] Wire to backend (served from GET / on same port 8000)
- [x] Confirm full end-to-end: UI served, healthz OK, SSE stream live
- **Checkpoint:** working demo, question in → streamed answer out ✅
  - GET / → WASSCE/BECE Offline Tutor HTML
  - GET /healthz → {"status":"ok","model":"SmolLM2-1.7B-Instruct"}
  - POST /ask → SSE meta+tokens+done confirmed in Step 4

## 6. Robustness pass
- [x] Empty input → 400 "Question must not be empty."
- [x] Whitespace-only input → 400 "Question must not be empty."
- [x] Very long input (5000 chars) → 400 "exceeds maximum length"
- [x] Non-math gibberish → answered gracefully, no crash
- [x] Emoji-only input → answered gracefully, no crash
- [x] 20 varied WASSCE/BECE prompts → all returned answers, zero crashes/OOMs
- [x] Fix anything that crashes or OOMs — none found
- **Checkpoint:** 20+ varied prompts, zero crashes/OOMs ✅
- [x] Picked 2 strongest prompts for metadata.json test_prompts:
  - tp_001: "Solve x^2 - 7x + 12 = 0 by factorization" (WASSCE Math)
  - tp_002: "A 12V battery connected to 4Ω resistor, calculate current" (WASSCE Science)

## 7. Official profiling
- [ ] Run:
  ```bash
  bash download_model.sh
  adtc-profiler run --submission . --mode participant --output submission.json --skip-accuracy
  cat submission.json
  ```
- [ ] Record Sperf and Seff numbers into `REPORT.md`
- [ ] Revisit quantization now if RAM/throughput is concerning
- **Checkpoint:** real Sperf/Seff numbers, not estimates

## 8. Report, video, repo cleanup
- [ ] Fill in `REPORT.md` fully (problem, design decisions, constraints,
      tools, benchmarks, screenshots/clips)
- [ ] Fill in every placeholder in `metadata.json` — no field left generic
- [ ] Record ≤2 minute demo video
- [ ] Confirm `.gitignore` excludes `model/` and `*.gguf`
- [ ] Fresh-clone test on a clean checkout: `download_model.sh` runs without
      errors, downloaded file is valid GGUF, path matches
      `_runtime.model_path` exactly
- **Checkpoint:** a stranger could clone and run this with zero manual fixes

## Fallback trigger
If after ~6–8 hours of Step 2 the model can't reliably solve WASSCE/BECE
problems even with RAG: pivot to Offline Coding Tutor, same architecture,
swap corpus + system prompt only. Log the pivot decision in `DECISIONS.md`.
