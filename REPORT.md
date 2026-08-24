# REPORT.md — WASSCE/BECE Offline Math & Science Tutor

## Problem
Students preparing for WASSCE and BECE exams across Nigeria, Ghana, Sierra
Leone, Liberia, and The Gambia often lack reliable, always-available help
with math and science problem-solving — especially outside major cities
where internet connectivity is unstable or costly. Existing AI tutoring
tools assume cloud connectivity, which excludes exactly the students who
would benefit most.

## Constraints
- **Power/compute:** must run entirely on a commodity laptop matching the
  ADTC Standard Laptop profile — Intel i5 10th–12th gen / AMD Ryzen 5
  3000–5000, 8GB RAM (7GB hard ceiling during evaluation), integrated
  graphics only, no discrete GPU at inference time.
- **Connectivity:** zero network calls permitted during inference/evaluation.
  Demonstrated by running with wifi disabled.
- **Data:** corpus limited to sourced, rights-clear WASSCE/BECE past
  questions (see Design Decisions below) — no unverified copyrighted
  textbook content.

## Design Decisions

### Domain selection
Evaluated six domain-scoped concepts (Agriculture, Coding, SME Assistant,
Clinical Triage, Autonomous Agents, and Math & Science) before selecting
Math & Scientific Reasoning. Math is one of the only domains where accuracy
is self-verifiable before demo day — a solved equation is either right or
wrong — which directly de-risks the accuracy-weighted portion of the score.
It also produces the most concrete, substantiable African Use Case Bonus
claim: the corpus is built from real exams sat by millions of students
across five countries, not a generic "helps African students" framing.

Full comparison table: see DECISIONS.md.

### Base model and quantization
Three candidates were evaluated with 5 WASSCE/BECE questions each (CPU-only,
Q4_K_M, no RAG) — see `DECISIONS.md` for the full comparison table.

**SmolLM2-1.7B-Instruct Q4_K_M** was chosen:
- Answered all 5/5 test questions correctly with step-by-step working
- 2.5 t/s average throughput and 1,346 MB peak RAM on the dev machine
- Gemma-2-2B answered only 1/5 within the time limit, used 1,948 MB peak RAM
- SmolLM2's 1.7B parameter count stays comfortably under the 7GB RAM ceiling
  even with retrieval context added to the prompt

**Q4_K_M quantization** was retained after profiling: peak RSS measured at
1,291 MB — leaving nearly 5.7 GB of headroom under the 7GB hard ceiling.
A lighter quantization (Q3_K_M) would save ~200 MB but risks answer quality
regression, which the scoring weights (accuracy 50%) do not justify.

### RAG over fine-tuning
Chose retrieval-augmented generation over the fixed WASSCE/BECE corpus
rather than fine-tuning the base model, given the build time available.
Fine-tuning carries higher time cost and less certain accuracy gain in this
window; RAG grounds answers in real past questions with far less risk.

## Tools used
- llama.cpp / GGUF + llama-cpp-python for on-device inference (required runtime)
- `adtc-profiler` for official Sperf/Seff measurement
- scikit-learn TF-IDF + cosine similarity for retrieval (offline, zero deps)
- sentence-transformers `all-MiniLM-L6-v2` cached locally (embedding fallback)
- FastAPI + SSE for the local inference server (Step 4)

## Benchmarks
Measured with `adtc-profiler run --submission . --mode participant --skip-accuracy`.
Only Sperf and Seff are self-reported; accuracy is judged centrally by the
organizers running the actual model — do not self-report or claim a score.

**Development machine:** Intel Core i7-3667U @ 2.00GHz, 8GB RAM, macOS 14.8.4.
Numbers on the ADTC Standard Laptop (i5 10th–12th gen / Ryzen 5) may differ.

| Metric | Value |
|---|---|
| Peak RAM / Seff | 1291 MB (1.26 GB) |
| Tokens/sec / Sperf | 1.8 t/s |
| First token latency | 63,737 ms (63.7 s) — cold start, model load included |
| Thermal throttling | None |
| params_match | ✅ true (1,711,376,384 params) |

## Screenshots / clips
Insert screenshots or short clips of the build in action here.

## African Use Case Bonus claim
This project's corpus consists of 50 original questions written to match
the format, syllabus, and difficulty levels of WASSCE (West African Senior
School Certificate Examination) and BECE (Basic Education Certificate
Examination) — the actual exams sat by millions of students across Nigeria,
Ghana, Sierra Leone, Liberia, and The Gambia. The content is hand-curated
original material; it is not sourced from or adapted from actual past papers.
The use case is grounded in a real, widely-taken regional examination system,
not a generic claim.

The optional LAN classroom mode (see Design Decisions above) directly
addresses a second real-world constraint specific to this region: shared
hardware. A single laptop running WASSCE Sage can serve an entire classroom
of students over local WiFi, with no internet dependency and no per-device
installation. This extends the African use case from individual offline access
to classroom-scale access on shared resources.
