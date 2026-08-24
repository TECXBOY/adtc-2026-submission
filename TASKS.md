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
- [ ] Build chat interface
- [ ] Wire to backend
- [ ] Confirm full end-to-end flow with streaming output
- **Checkpoint:** working demo, question in → streamed answer out

## 6. Robustness pass
- [ ] Empty input
- [ ] Very long input
- [ ] Non-math input
- [ ] Repeated rapid requests
- [ ] Fix anything that crashes or OOMs
- **Checkpoint:** 20+ varied prompts, zero crashes/OOMs
- [ ] From this validated set, pick the 2 strongest prompts for
      `metadata.json`'s `test_prompts` array

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
