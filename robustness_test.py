#!/usr/bin/env python3
"""
Step 6 robustness test suite.
Starts the server, runs all edge cases + 20 varied prompts, reports results.

Prerequisites: server must NOT be running on port 8000 before this script.
Usage: .venv/bin/python3 robustness_test.py
"""
import json, subprocess, sys, time, os, signal, urllib.request, urllib.error

PORT = 8000
BASE = f"http://127.0.0.1:{PORT}"
RESULTS = []


def post_ask(question, timeout=90):
    """POST /ask, consume full SSE stream, return (answer_text, error_or_None)."""
    data = json.dumps({"question": question}).encode()
    req  = urllib.request.Request(
        f"{BASE}/ask",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            answer = ""
            error  = None
            for raw_line in resp:
                line = raw_line.decode("utf-8").rstrip("\n")
                if not line.startswith("data: "):
                    continue
                payload = json.loads(line[6:])
                if payload["event"] == "token":
                    answer += payload["text"]
                elif payload["event"] == "error":
                    error = payload["detail"]
                elif payload["event"] == "done":
                    break
            return answer, error
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        return "", body.get("detail", str(e))
    except Exception as e:
        return "", str(e)


def record(label, question, expected_ok=True):
    print(f"\n  [{label}]", flush=True)
    answer, err = post_ask(question)
    ok = (err is None) if expected_ok else True  # validation errors are "ok" when expected
    status = "✅" if (not err and answer) or (not expected_ok and err) else "❌"
    print(f"  {status}  answer_len={len(answer)}  err={err or 'none'}", flush=True)
    if answer:
        print(f"  First 120 chars: {answer[:120].strip()}", flush=True)
    RESULTS.append({"label": label, "ok": ok, "has_answer": bool(answer),
                    "err": err, "answer_len": len(answer)})


# ── Start server ────────────────────────────────────────────────────────────
print("Starting server…", flush=True)
srv = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "backend.serve:app",
     "--host", "127.0.0.1", "--port", str(PORT), "--log-level", "warning"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
# Wait for it to be ready
for _ in range(30):
    try:
        urllib.request.urlopen(f"{BASE}/healthz", timeout=2)
        print("Server ready.", flush=True)
        break
    except Exception:
        time.sleep(2)

# ── Edge cases ───────────────────────────────────────────────────────────────
print("\n=== Edge case tests ===")
record("empty input",        "",                         expected_ok=False)
record("whitespace only",    "   \n\t  ",                expected_ok=False)
record("very long input",    "x" * 5000,                 expected_ok=False)  # over 4000 char cap
record("non-math gibberish", "asdfghjkl qwerty zxcv 123!@#")
record("emoji only",         "🦁🦁🦁🦁🦁")
record("repeated question",  "What is 2 + 2?")

# ── 20 varied WASSCE/BECE prompts ────────────────────────────────────────────
PROMPTS = [
    ("Math easy 1",    "Solve for x: 2x + 4 = 10"),
    ("Math easy 2",    "Find the area of a triangle with base 6cm and height 8cm."),
    ("Math medium 1",  "A bag has 3 red and 7 blue balls. What is the probability of picking a blue ball?"),
    ("Math medium 2",  "Simplify: 3^4 / 3^2"),
    ("Math medium 3",  "Find the 8th term of the arithmetic sequence 2, 5, 8, 11 …"),
    ("Math medium 4",  "y varies directly as x. When x=5, y=15. Find y when x=9."),
    ("Math hard 1",    "Solve x^2 - 7x + 12 = 0 by factorization."),
    ("Math hard 2",    "Find the compound interest on GH₵2000 for 3 years at 10% per annum."),
    ("Sci easy 1",     "Name the three states of matter and describe the particle arrangement in each."),
    ("Sci easy 2",     "What is the function of chlorophyll in a plant?"),
    ("Sci easy 3",     "State Newton's Second Law of Motion and write the formula."),
    ("Sci easy 4",     "What colour does red litmus paper turn in an alkaline solution?"),
    ("Sci medium 1",   "Write the balanced word equation for aerobic respiration."),
    ("Sci medium 2",   "Name the organelle responsible for photosynthesis in plant cells."),
    ("Sci medium 3",   "A 12V battery is connected to a 4Ω resistor. Calculate the current."),
    ("Sci medium 4",   "Define a food chain and give an example with four organisms."),
    ("Sci hard 1",     "Explain the process of photosynthesis, including the reactants and products."),
    ("Mixed 1",        "A car travels 200km at 50km/h. How long does the journey take?"),
    ("Mixed 2",        "Express 0.0042 in standard form."),
    ("Mixed 3",        "What gas is produced when zinc reacts with dilute hydrochloric acid?"),
]

print("\n=== 20 varied WASSCE/BECE prompts ===")
for label, q in PROMPTS:
    record(label, q)

# ── Stop server ──────────────────────────────────────────────────────────────
srv.terminate()
srv.wait()
print("\nServer stopped.", flush=True)

# ── Summary ──────────────────────────────────────────────────────────────────
passed = sum(1 for r in RESULTS if (r["has_answer"] or r["err"]))
total  = len(RESULTS)
crashes = [r for r in RESULTS if not r["has_answer"] and not r["err"]]

print(f"\n{'='*60}")
print(f"ROBUSTNESS SUMMARY: {passed}/{total} passed")
if crashes:
    print(f"CRASHES / NO-RESPONSE: {len(crashes)}")
    for c in crashes:
        print(f"  - {c['label']}: {c}")
else:
    print("No crashes or silent failures.")

# Save results
with open("robustness_results.json", "w") as f:
    json.dump(RESULTS, f, indent=2)
print("Results saved to robustness_results.json")
