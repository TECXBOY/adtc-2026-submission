#!/usr/bin/env python3
"""
Step 2 eval — single model, all 5 questions, streams progress.
Usage: python3 eval_single.py <model_path> <model_name>
"""
import sys, time, resource, json, signal

def alarm_handler(sig, frame):
    raise TimeoutError()
signal.signal(signal.SIGALRM, alarm_handler)

model_path = sys.argv[1]
model_name = sys.argv[2]

QUESTIONS = [
    ("BECE Geometry",    "A ladder 10m long leans against a vertical wall. The foot of the ladder is 6m from the wall. Find the height at which the ladder touches the wall. Show step-by-step working."),
    ("BECE Algebra",     "Solve for x: 3x + 7 = 22. Show step-by-step working."),
    ("WASSCE Commerce",  "A trader bought 50 oranges at 3 naira each and sold them at 5 naira each. Calculate the profit percent. Show step-by-step working."),
    ("WASSCE Physics",   "State Newton's second law of motion and write its mathematical expression."),
    ("WASSCE Chemistry", "Write the electron configuration of Calcium (atomic number 20)."),
]

SYSTEM = "You are a WASSCE/BECE exam tutor. Answer with clear step-by-step working. Be concise."

from llama_cpp import Llama

print(f"\n=== {model_name} ===", flush=True)
rss0 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
llm = Llama(model_path=model_path, n_ctx=512, n_threads=4, n_gpu_layers=0, verbose=False)
rss1 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
ram_load_mb = rss1 / 1e6  # macOS: bytes
print(f"RAM after load: {ram_load_mb:.0f} MB", flush=True)

results = []
for label, question in QUESTIONS:
    print(f"\n[{label}]", flush=True)
    signal.alarm(120)  # 2-min per question hard limit
    try:
        t0 = time.time()
        # Gemma-2 rejects a system role — fold it into the first user turn
        try:
            resp = llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user",   "content": question},
                ],
                max_tokens=200, temperature=0.2, stream=False,
            )
        except Exception:
            resp = llm.create_chat_completion(
                messages=[
                    {"role": "user", "content": f"{SYSTEM}\n\n{question}"},
                ],
                max_tokens=200, temperature=0.2, stream=False,
            )
        elapsed = time.time() - t0
        signal.alarm(0)
        ans = resp["choices"][0]["message"]["content"]
        n   = resp["usage"]["completion_tokens"]
        tps = n / elapsed
        ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
        print(f"A: {ans[:300]}", flush=True)
        print(f"→ {n} tok / {elapsed:.1f}s = {tps:.1f} t/s | RAM {ram:.0f} MB", flush=True)
        results.append({"label": label, "tps": tps, "ram_mb": ram, "ok": True, "answer": ans})
    except TimeoutError:
        signal.alarm(0)
        print("TIMED OUT — skipping", flush=True)
        results.append({"label": label, "tps": 0, "ram_mb": 0, "ok": False})

del llm

avg_tps  = sum(r["tps"] for r in results if r["ok"]) / max(1, sum(1 for r in results if r["ok"]))
peak_ram = max((r["ram_mb"] for r in results if r["ok"]), default=0)

print(f"\n--- SUMMARY: {model_name} ---")
print(f"Avg t/s: {avg_tps:.1f}")
print(f"Peak RAM: {peak_ram:.0f} MB")

out = {"model": model_name, "avg_tps": round(avg_tps,1), "peak_ram_mb": round(peak_ram), "results": results}
out_path = f"eval_results_{model_name.replace(' ','_').replace('/','_')}.json"
with open(out_path, "w") as f:
    json.dump(out, f, indent=2)
print(f"Results saved to {out_path}")
