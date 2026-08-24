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
Fill in once Step 2 is complete — reference the candidate comparison table
in DECISIONS.md. State the model chosen, why, and the quantization level
selected with the accuracy/RAM tradeoff data that justified it.

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
Fill in from the real `adtc-profiler` run — do not estimate.
Only Sperf and Seff are self-reported; accuracy is judged centrally by the
organizers running the actual model — do not self-report or claim a score.

| Metric | Value |
|---|---|
| Peak RAM (Seff) | |
| Tokens/sec (Sperf) | |

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
