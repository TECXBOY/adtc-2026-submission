# WASSCE Sage

## Inspiration

Millions of students across West Africa prepare for WASSCE and BECE examinations, yet most AI tutoring tools assume continuous access to the internet. For students dealing with unreliable, expensive, or unavailable connectivity, that assumption creates a simple problem: the AI tutor disappears when the connection does.

We wanted to remove that dependency completely.

**WASSCE Sage** was built around one idea: **useful AI tutoring should not require the cloud.**

Instead of sending a student's question to a remote API, we put the intelligence directly on the laptop. The result is an AI tutor that operates with **zero internet connectivity**, while being grounded in the mathematics and science content students actually encounter in WASSCE and BECE preparation.

The offline constraint became the foundation of the project rather than a limitation.

---

## What it does

**WASSCE Sage** is an offline, on-device Mathematics and Integrated Science tutor designed for WASSCE and BECE preparation.

A student types a question — or selects one of the suggested prompts — and the system retrieves relevant material from a **local corpus of 50 hand-curated WASSCE/BECE-style questions** before generating a step-by-step worked solution.

It does not simply return an answer. It explains the method, shows the calculations, and presents the result in a form a student can learn from.

For example, given:

> *A trader bought 120 oranges at GH₵2.50 each. She sold 80 at GH₵4.00 each and the remaining 40 at GH₵1.50 each due to spoilage. Calculate her overall profit or loss as a percentage of the cost price.*

WASSCE Sage works through it:

```
Cost price  = 120 × GH₵2.50 = GH₵300
Revenue (80) = 80 × GH₵4.00 = GH₵320
Revenue (40) = 40 × GH₵1.50 = GH₵60
Total revenue = GH₵380
Profit = GH₵380 − GH₵300 = GH₵80
Profit % = (80 ÷ 300) × 100 = 26.67%
```

That interaction runs **without an internet connection and without a cloud AI API**.

---

## How we built it

WASSCE Sage is composed of three locally-running components.

### 1. Quantized local language model

We selected **SmolLM2-1.7B-Instruct**, quantized to **GGUF Q4_K_M**, running via `llama.cpp` for CPU-only inference.

We evaluated **three candidate models** — SmolLM2-1.7B, Gemma-2-2B, and Phi-3.5-mini — against five WASSCE/BECE-style test questions each (no RAG, Q4_K_M, CPU-only):

| Model | Answer quality | Avg t/s | Peak RAM |
|---|---|---|---|
| **SmolLM2-1.7B Q4_K_M** | **5/5 correct** | **2.5** | **1,346 MB** |
| Gemma-2-2B Q4_K_M | 1/5 within timeout | 1.6 | 1,948 MB |
| Phi-3.5-mini Q4_K_M | Not testable (download failed) | — | — |

SmolLM2 was chosen because it answered all five questions correctly with clear step-by-step working, ran 56% faster than Gemma, and used 31% less RAM. Gemma-2 timed out on four of five questions at the 120-second cut-off — unusable at this CPU speed.

The goal was not to fit the largest model. It was to find the best balance between answer quality, inference speed, and memory within the competition's 7 GB hard ceiling.

### 2. Local retrieval-augmented generation

We built a local RAG pipeline using **TF-IDF + cosine similarity** (scikit-learn), indexed over a hand-curated corpus of **50 WASSCE/BECE-style questions** — 30 Mathematics and 20 Integrated Science — covering core syllabus topics including algebra, geometry, mensuration, statistics, probability, trigonometry, sequences, forces, electricity, chemistry, and biology.

When a student asks a question, the system retrieves the top-3 most relevant corpus entries locally and provides them as context to the model before generation.

This gives the model a focused, exam-relevant knowledge environment rather than relying on its base training alone.

**Retrieval is entirely local.** There is no remote vector database, cloud search API, or external knowledge call during inference.

We chose TF-IDF over a sentence-transformer embedding model for two reasons: it has zero network dependencies at runtime, and for a 50-document corpus it retrieves correctly while loading in milliseconds rather than tens of seconds.

### 3. Lightweight local interface

A lightweight web interface provides the student-facing experience. The backend is a **FastAPI server** exposing a `POST /ask` endpoint that streams tokens over SSE. The frontend is a single HTML file served from the same process — the student interface is a pure HTTP client of the local server.

The interface streams the model's response token by token, shows which corpus entries were retrieved, and handles edge cases cleanly: empty input is rejected immediately, oversized input is blocked at 4,000 characters, and non-math gibberish is met with a graceful response rather than a crash.

### The complete pipeline

```
Student Question
      ↓
TF-IDF Retrieval (local, ~5ms)
      ↓
Top-3 Relevant Corpus Entries
      ↓
RAG Prompt Construction
      ↓
SmolLM2-1.7B-Instruct Q4_K_M
      ↓
llama.cpp CPU Inference (streaming)
      ↓
Step-by-Step Worked Solution
```

No cloud API. No external inference server. No internet dependency. No student data leaving the device.

We validated the complete pipeline with networking disabled and benchmarked using the official `adtc-profiler`.

---

## Why Mathematics and Scientific Reasoning?

We evaluated six domain options: Agriculture, Coding, SME Assistant, Clinical Triage, Autonomous Agents, and Math & Science.

We chose **Mathematics and Scientific Reasoning** for two concrete reasons.

First, **objective evaluation**. A mathematical solution has a verifiable result — a solved equation is right or wrong. That let us evaluate the system ourselves against real questions, rather than relying entirely on subjective judgments about whether an answer sounded plausible.

Second, **a substantiable African use case claim**. The corpus is written to match the actual exams sat by millions of students across Nigeria, Ghana, Sierra Leone, Liberia, and The Gambia. That is a specific, verifiable claim, not a generic "helps African students" framing.

---

## Challenges

### Model selection under hardware constraints

We ran quantitative comparisons rather than assuming the largest model would win. Gemma-2-2B — a reasonable choice on paper — was completely unusable in practice: it timed out on four of five test questions at CPU-only inference speeds. SmolLM2-1.7B completed all five correctly and ran 56% faster.

The lesson: on constrained hardware, measured behavior matters more than parameter count.

### Retrieval without external dependencies

Sentence-transformer embedding models are the standard choice for semantic retrieval, but they require network access on first use to download weights and have a 10+ second cold-start time. For an offline-first submission those are real problems.

We switched to TF-IDF + cosine similarity: zero network calls, millisecond load times, and retrieval quality that is entirely adequate for a 50-document corpus where queries and documents share domain vocabulary.

### Robustness under edge cases

A crash or OOM during judging zeroes the entire score. We stress-tested the complete pipeline against empty input, inputs over 4,000 characters, emoji-only input, nonsense strings, and 20+ varied WASSCE/BECE prompts. Zero crashes, zero silent failures.

---

## What we learned

Bigger does not automatically mean better on constrained hardware.

SmolLM2-1.7B at Q4_K_M produced correct, well-structured worked solutions while consuming only 1,291 MB peak RAM — leaving 5.7 GB of headroom under the competition ceiling. The formally "stronger" 2.6B Gemma-2 model was slower, used more memory, and failed on most test questions within the time limit.

We also learned that building for offline changes system architecture from the ground up. When there is no cloud fallback, every dependency matters. The retrieval approach, the model runtime, the corpus format, and the serving layer all have to work locally and reliably. Performance cannot be optimized one component at a time — the entire pipeline has to be designed around the constraint.

That constraint turned out to be an asset. Removing the internet dependency gives WASSCE Sage something cloud-based tutoring tools cannot offer in the same way: the answer is always available, the student's questions never leave the device, and the system works identically whether the student is in Lagos, Accra, or a village with no data signal.

**If the intelligence lives on the device, the internet stops being a prerequisite for access to it.**
