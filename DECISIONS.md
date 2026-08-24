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

## Corpus sourcing — [CONFIRM WITH HUMAN]
**Question:** Which WASSCE/BECE past-question source(s) will be used, and
what is their redistribution license?
**Options considered:**
- Official WAEC released past questions
- Named OER (open educational resource) source
**Decision:** PENDING — confirm before Step 3.
**Reasoning:** fill in once confirmed
**Status:** Blocking Step 3.

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

## Fallback pivot (only fill in if triggered)
**Triggered:** Yes / No
**If yes — reasoning and what changed:** fill in
