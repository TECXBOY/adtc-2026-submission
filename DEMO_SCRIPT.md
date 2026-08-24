# Demo Video Script — WASSCE/BECE Offline Tutor
# ADTC 2026 · Target length: ≤ 2 minutes

Follow each section in order. All terminal commands are copy-paste ready.
Record your screen + mic (or captions only — both work).

---

## Before you hit record

Open these in advance so nothing loads slowly on camera:
- Terminal, cd'd into the repo
- Browser at http://127.0.0.1:8000 (do NOT open yet — keep tab blank)
- System Settings / Network panel (to show WiFi toggle)
- A second terminal tab ready to cat submission.json

Make sure the server is NOT already running.

---

## 0:00 – 0:15 · Cold open — prove offline first

**On screen:** macOS System Settings → Network (or the menu-bar WiFi icon)
Turn WiFi OFF on camera. Let it visibly disconnect.

Voiceover / caption:
  "Running fully offline — no internet connection."

Leave WiFi off for the entire recording. Do not turn it back on.

---

## 0:15 – 0:35 · Launch the app

Switch to your terminal. Run:

```bash
cd ~/developnment/Orbit/adtc-2026-submission
.venv/bin/python3 -m uvicorn backend.serve:app \
  --host 127.0.0.1 --port 8000 \
  --log-level warning
```

Wait for the cursor to settle (model load takes ~5–10s, keep that on screen —
it shows the cold-start, not a pre-warmed state).

Switch to the browser tab and navigate to:
  http://127.0.0.1:8000

The status dot in the header should turn green ("ready").

Type this question into the input box and hit Enter:
  "A trader bought 120 oranges at GH₵2.50 each. She sold 80 at GH₵4.00 each
   and the remaining 40 at GH₵1.50 each due to spoilage. Calculate her overall
   profit or loss and express it as a percentage of the cost price."

Keep the camera on the chat window — let the tokens stream in visibly.

Caption (optional, appears as tokens arrive):
  "Answer grounded in retrieved WASSCE-style questions"

---

## 0:35 – 1:10 · Full answer resolves

Stay on the browser. Let the complete step-by-step solution render fully.
Scroll down slowly if the answer is long — show the working, not just the final line.

Expected answer (verify this matches before recording):

  Cost price = 120 × GH₵2.50 = GH₵300
  Revenue (80 oranges) = 80 × GH₵4.00 = GH₵320
  Revenue (40 oranges) = 40 × GH₵1.50 = GH₵60
  Total revenue = GH₵380
  Profit = GH₵380 − GH₵300 = GH₵80
  Profit % = (80 / 300) × 100 = 26.67%

You do not need to read this aloud — the on-screen text does the work.

---

## 1:10 – 1:35 · Second question — Integrated Science

Clear the input box (or just type over it). Send this question:
  "State Newton's Second Law of Motion, write its mathematical expression,
   and explain what each term means."

Again let the answer stream in fully.
This cut proves domain breadth (Math → Science) in one shot.

---

## 1:35 – 1:50 · Robustness — one quick edge case

Click the input box, leave it empty, hit Enter (or the send button).
The UI should show the validation message immediately — no crash, no spinner.

You can say or caption:
  "Empty input rejected cleanly."

Optional second shot: type random gibberish ("asdfgh 123!@#") and send.
Show it responds gracefully rather than crashing.

---

## 1:50 – 2:00 · Close on the profiler numbers

Switch to your second terminal tab and run:

```bash
cat ~/developnment/Orbit/adtc-2026-submission/submission.json \
  | python3 -m json.tool \
  | grep -A6 '"throughput"' && \
  cat ~/developnment/Orbit/adtc-2026-submission/submission.json \
  | python3 -m json.tool \
  | grep -A4 '"memory"'
```

This will print something like:

    "throughput": {
        "tokens_per_second_generation": 1.8,
        "first_token_latency_ms": 63736.52,
        ...
    },
    "memory": {
        "peak_rss_mb": 1291.56,
        ...
    }

Hold that output on screen for ~5 seconds. No voiceover needed.
End recording here.

---

## After recording

1. Turn WiFi back on.
2. Stop the server with Ctrl-C.
3. Export the video (MP4, ≤ 2 min, reasonable resolution — 1080p is fine).
4. Add the video link / file to REPORT.md under "Screenshots / clips":

```bash
cd ~/developnment/Orbit/adtc-2026-submission
# Edit REPORT.md → Screenshots / clips section, add:
# Demo video: [link or filename]

git add REPORT.md
git commit -m "Add demo video link to REPORT.md"
git push
```

---

## Checklist before submitting

- [ ] WiFi visibly off at the start of the video
- [ ] Server launched cold (not pre-warmed) on camera
- [ ] Math question streams token by token
- [ ] Full step-by-step answer visible
- [ ] Science question answered (different domain shown)
- [ ] Edge case (empty input) handled cleanly
- [ ] Profiler output (Sperf 1.8, Seff 1291.56 MB) visible at the end
- [ ] Video is ≤ 2 minutes
- [ ] Video link added to REPORT.md and pushed
