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
**Candidates tested:**

| Model | Params | GGUF avail. | Raw accuracy (n=__) | Tokens/sec | Peak RAM | License OK? |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |
| | | | | | | |

**Decision:** fill in once Step 2 complete
**Reasoning:** fill in — should reference the table above, not intuition
**Status:** Pending Step 2.

---

## Quantization level — [DECIDE]
**Levels tested:** Q4_K_M (baseline), plus one lighter and one heavier
**Results:**

| Quant level | Accuracy delta vs. baseline | Peak RAM | Tokens/sec |
|---|---|---|---|
| | | | |

**Decision:** fill in
**Reasoning:** fill in — accuracy is judged centrally by the organizers
(not self-reported); S_acc is weighted 2.5x higher than S_eff, so RAM
savings alone should not justify a regression in the model's answer quality
**Status:** Pending Step 2/7.

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
