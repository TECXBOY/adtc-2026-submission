#!/usr/bin/env python3
"""
Step 2 candidate evaluation — run 5 WASSCE/BECE test questions against each
model, capture tokens/sec and peak RSS, print a summary table.
Usage: python3 eval_candidates.py
"""

import time, resource, sys, textwrap
from llama_cpp import Llama

CANDIDATES = [
    {
        "name": "SmolLM2-1.7B-Instruct Q4_K_M",
        "path": "model/smollm2-1.7b-instruct-q4_k_m.gguf",
    },
    {
        "name": "Gemma-2-2B-it Q4_K_M",
        "path": "model/gemma-2-2b-it-q4_k_m.gguf",
    },
]

QUESTIONS = [
    ("BECE Geometry",    "A ladder 10m long leans against a vertical wall. The foot of the ladder is 6m from the wall. Find the height at which the ladder touches the wall. Show your working step by step."),
    ("BECE Algebra",     "Solve for x: 3x + 7 = 22. Show your working step by step."),
    ("WASSCE Commerce",  "A trader bought 50 oranges at 3 naira each and sold them at 5 naira each. Calculate the profit percent. Show your working step by step."),
    ("WASSCE Physics",   "State Newton's second law of motion and write its mathematical expression. Explain each term."),
    ("WASSCE Chemistry", "Write the electron configuration of Calcium (atomic number 20) and explain which group and period it belongs to."),
]

SYSTEM = (
    "You are a WASSCE/BECE exam tutor. "
    "Answer every question with clear step-by-step working. "
    "Be concise but complete."
)

def peak_ram_mb():
    # macOS: ru_maxrss is bytes; Linux: kilobytes
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return rss / 1e6 if sys.platform == "darwin" else rss / 1e3

def run_candidate(cand):
    print(f"\n{'='*70}")
    print(f"MODEL: {cand['name']}")
    print(f"{'='*70}")

    ram_before = peak_ram_mb()
    llm = Llama(
        model_path=cand["path"],
        n_ctx=2048,
        n_threads=4,
        n_gpu_layers=0,   # CPU-only
        verbose=False,
    )
    ram_after_load = peak_ram_mb()
    print(f"  RAM after load: {ram_after_load:.0f} MB  (delta: +{ram_after_load - ram_before:.0f} MB)")

    results = []
    for label, question in QUESTIONS:
        messages = [
            {"role": "system", "content": SYSTEM},
            {"role": "user",   "content": question},
        ]
        t0 = time.time()
        resp = llm.create_chat_completion(
            messages=messages,
            max_tokens=400,
            temperature=0.2,
            stream=False,
        )
        elapsed = time.time() - t0

        answer = resp["choices"][0]["message"]["content"]
        usage  = resp.get("usage", {})
        n_prompt    = usage.get("prompt_tokens", 0)
        n_generated = usage.get("completion_tokens", 0)
        tps = n_generated / elapsed if elapsed > 0 else 0
        ram_now = peak_ram_mb()

        results.append({
            "label": label,
            "tps": tps,
            "ram_mb": ram_now,
            "n_generated": n_generated,
            "elapsed": elapsed,
            "answer": answer,
        })

        print(f"\n  [{label}]")
        print(f"  Q: {question[:80]}...")
        print(f"  A (first 300 chars): {answer[:300].strip()}")
        print(f"  → {n_generated} tokens in {elapsed:.1f}s = {tps:.1f} t/s | RAM: {ram_now:.0f} MB")

    del llm  # free model before next candidate

    avg_tps  = sum(r["tps"]    for r in results) / len(results)
    peak_ram = max(r["ram_mb"] for r in results)
    return {"name": cand["name"], "avg_tps": avg_tps, "peak_ram_mb": peak_ram, "results": results}

def main():
    summaries = []
    for cand in CANDIDATES:
        try:
            s = run_candidate(cand)
            summaries.append(s)
        except Exception as e:
            print(f"\nERROR loading {cand['name']}: {e}")

    print(f"\n\n{'='*70}")
    print("SUMMARY TABLE")
    print(f"{'='*70}")
    print(f"{'Model':<35} {'Avg t/s':>10} {'Peak RAM (MB)':>14}")
    print(f"{'-'*35} {'-'*10} {'-'*14}")
    for s in summaries:
        print(f"{s['name']:<35} {s['avg_tps']:>10.1f} {s['peak_ram_mb']:>14.0f}")
    print()

if __name__ == "__main__":
    main()
