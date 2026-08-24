# Decision Log

Every [DECIDE] point gets an entry here, made in real time as Bob builds —
this becomes the backbone of REPORT.md's design decisions section. Every
[CONFIRM WITH HUMAN] point gets an entry once resolved.

---

## Domain selection (pre-decided, included for report completeness)
**Decision:** Math & Scientific Reasoning (WASSCE/BECE), not Agriculture,
Coding, SME Assistant, Clinical Triage, or Autonomous Agents.
**Reasoning:** Math is self-verifiable before demo day, directly de-risking
the 50%-weighted accuracy score. The African Use Case Bonus claim is
concrete: corpus is real exams sat by millions of students across five
countries.
**Status:** Final.

---

## Corpus sourcing — [CONFIRMED] ✅
**Source:** 50 original questions hand-written from scratch to match real
WASSCE/BECE syllabus topics, phrasing conventions, and difficulty levels.
Not sourced from or adapted from actual past papers.
**License:** None required — original content, safe to commit directly.
**Format:** `corpus/wassce_bece_questions.jsonl`, 50 records.
Each record carries `"source": "hand-curated"` for provenance tracking.
**Coverage:** 30 Mathematics + 20 Integrated Science, spanning BECE and
WASSCE levels, core topics (algebra, geometry, mensuration, statistics,
probability, trigonometry, sequences, states of matter, photosynthesis,
forces, electricity, chemistry, biology).
**Decision:** Use this hand-curated set as the corpus seed. Treat as the
floor — expand topic/difficulty coverage if time allows after retrieval
is validated (Step 3 checkpoint).
**Reasoning:** Avoids any redistribution licensing risk while still
grounding the African Use Case Bonus claim concretely — these questions
are written to match the actual exams sat by millions of students across
Nigeria, Ghana, Sierra Leone, Liberia, and The Gambia.
**Status:** Final. ✅

---

## Base model selection — [DECIDE]
**Candidates tested:** 5 WASSCE/BECE questions (geometry, algebra, commerce,
physics, chemistry) — raw inference, no RAG, Q4_K_M quant, n_ctx=512,
n_threads=4, CPU-only, macOS M-series (relative baseline; eval machine will
score differently in absolute t/s terms).

| Model | Params | GGUF avail. | Answer quality | Avg t/s | Peak RAM | License OK? |
|---|---|---|---|---|---|---|
| SmolLM2-1.7B-Instruct Q4_K_M | 1.7B | ✅ bartowski | Correct, step-by-step on 5/5 | 2.5 | 1346 MB | ✅ Apache 2.0 |
| Gemma-2-2B-it Q4_K_M | 2.6B | ✅ bartowski | Correct on 1/5 (4 timed out at 120s) | 1.6 | 1948 MB | ✅ Gemma (permissive) |
| Phi-3.5-mini-instruct Q4_K_M | 3.8B | partial download | Not tested — download incomplete | — | — | ✅ MIT |

**Decision:** **SmolLM2-1.7B-Instruct Q4_K_M**
**Reasoning:** SmolLM2 answered all 5 test questions correctly with clear
step-by-step working, runs 56% faster than Gemma, and uses 31% less RAM.
Gemma-2 timed out on 4/5 questions at the 120-second limit — unusable at
this CPU speed. Phi-3.5 (3.8B) was not testable due to a partial download,
but at 3.8B it would consume more RAM than SmolLM2 with likely diminishing
returns given the score weighting (accuracy 50%, throughput 30%, RAM 20%).
SmolLM2 at 1346 MB peak leaves a safe margin under the 7GB ceiling.
**Status:** Final. ✅

---

## Quantization level — [DECIDE]
**Levels tested:** Q4_K_M only at Step 2. Step 7 (official profiling) will
determine whether a lighter quant (Q3_K_M) or heavier quant (Q5_K_M) is
warranted based on real Sperf/Seff numbers.
**Results:**

| Quant level | Answer quality | Peak RAM | Avg t/s |
|---|---|---|---|
| Q4_K_M (baseline) | 5/5 correct | 1346 MB | 2.5 |
| Q3_K_M | pending Step 7 | — | — |
| Q5_K_M | pending Step 7 | — | — |

**Decision:** Q4_K_M for now; revisit at Step 7 if Seff is tight
**Reasoning:** accuracy is judged centrally by the organizers
(not self-reported); S_acc is weighted 2.5x higher than S_eff, so RAM
savings alone do not justify a regression in answer quality.
**Status:** Provisional — confirm at Step 7.

---

## Scoring clarification (confirmed during scaffold phase)
Accuracy is **not** self-reported. Only Sperf (tokens/sec) and Seff (peak
RAM) are self-reported via `adtc-profiler`. Accuracy is judged centrally by
the organizers running the actual model against hidden test prompts.
Implication: do not claim or log an accuracy score anywhere in this repo.

---

## LAN classroom mode — [DECIDE]
**Decision:** Implement as an optional feature, default off.
**What was built:** A `lan_mode` flag in `config.yaml` (default `false`).
When `true`, the FastAPI server binds to `0.0.0.0` instead of `127.0.0.1`,
prints the laptop's LAN IP to the console on startup, and opens CORS to
allow any origin. A concurrency lock (`asyncio.Lock`) queues simultaneous
requests from multiple devices rather than allowing them to collide on the
single llama.cpp inference context. The frontend uses `window.location.origin`
instead of a hardcoded IP, so it works correctly from both localhost and LAN
clients without code changes.
**Reasoning:** Under-resourced schools across West Africa often have one
laptop per classroom, not one per student. LAN mode lets a teacher run the
tutor on that one laptop and serve it to students' phones or other devices
over classroom WiFi — still fully offline, no internet required. This was
possible with minimal extra code because the backend was already architected
as a standalone HTTP service (per BOB_ADDENDUM_pre-step4.md). The feature
directly strengthens the African Use Case Bonus claim beyond individual
offline access.
**Safety:** Default is `false`. The competition evaluation requires zero
network exposure — `lan_mode: true` would be disqualifying during judging.
The config comment, DECISIONS.md entry, and README all make this explicit.
`allow_network: false` remains a hard assertion that fires regardless of
`lan_mode` — it is a separate flag governing whether the server itself makes
outbound network calls (it never does).
**Status:** Implemented and tested from a second device. Default confirmed
`false` in committed config.yaml.

---

## Fallback pivot (only fill in if triggered)
**Triggered:** No
