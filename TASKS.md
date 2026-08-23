# Build Sequence — do not reorder

Each step must produce a runnable checkpoint with real output shown before
moving to the next. No speculative full-stack building.

## 1. Environment setup
- [x] Clone official ADTC 2026 submission template repo
- [ ] Install `adtc-profiler`: `pip install "git+https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler.git"`
- [ ] Confirm profiler runs against a placeholder/dummy model
- **Checkpoint:** profiler produces output on a dummy model

## 2. Model selection and quantization test
- [ ] Download 2–3 candidate small (1B–4B) instruct models in GGUF form
- [ ] Load each via llama.cpp locally
- [ ] Run raw WASSCE/BECE-style math questions, no RAG yet
- [ ] Record accuracy, tokens/sec, peak RAM per candidate
- [ ] Pick model empirically, log decision + numbers in `DECISIONS.md`
- **Checkpoint:** table of real numbers per candidate model

## 3. Corpus build
- [ ] Confirm corpus sourcing/licensing — [CONFIRM WITH HUMAN], do not skip
- [ ] Compile WASSCE/BECE past-question corpus
- [ ] Chunk corpus, build local embedding index
- [ ] Validate retrieval quality on a handful of test questions
- **Checkpoint:** retrieval returns relevant chunks for test queries

## 4. RAG + inference pipeline
- [ ] Wire retrieval into prompt construction
- [ ] Connect to chosen model
- [ ] Confirm grounded answers beat raw-model answers on step-2 test questions
- **Checkpoint:** side-by-side raw vs. RAG answers, RAG visibly better

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
