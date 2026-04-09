# Aegis Handoff Packets — Minimal Copy-Paste Between Roles

The three-role separation is what makes your research rigorous. But
copy-pasting long handoffs between conversations is friction. This
document defines compact handoff packets — the minimum information
each role needs, formatted for fast copy-paste.


## Why separate conversations matter

The Auditor works because it CAN'T see the Creator's reasoning.
The Analyst works because it DOESN'T know your hypothesis.
The separation is the methodology, not overhead.

A unified conversation is fine for exploring ideas and learning.
For real experiments that produce publishable results, use separate
conversations. The 30 seconds of copy-paste is the cheapest peer
review you'll ever get.


## When to use which

| Situation | Use |
|-----------|-----|
| Learning Aegis, exploring ideas | Companion (unified) |
| Quick one-off analysis | Companion (unified) |
| Real experiments you'll publish | Separate roles |
| Anything with pre-registration | Separate roles |
| Results that affect go/no-go decisions | Separate roles |

Rule of thumb: if the result matters, separate. If you're just
thinking, unified is fine.


## Compact handoff packets


### Creator → Auditor (paste this into the Auditor conversation)

```
AEGIS AUDIT REQUEST
Phase: [phase] | WU: [work unit]

[paste the complete script here]

Expected outputs: [list of files]
Calibration values used: [list any thresholds loaded from state]
```

That's it. Do NOT paste your reasoning, your hypothesis, or why
you made design choices. The Auditor should evaluate the script
cold. The less context, the better the audit.


### Auditor → Creator (paste this back into Creator conversation)

```
AUDIT RESULT: [PASS/FAIL] (iteration [N]/3)
Findings:
1. [severity] [description]
2. [severity] [description]
```

If FAIL, the Creator fixes and produces a new script. You paste
the new script back to the Auditor. Maximum 3 rounds.


### Colab output → Analyst (paste into Analyst conversation)

```
AEGIS RESULTS — [work unit]
[paste the Cell 3 output from Colab here — everything above
 the "copy this" line]
```

Do NOT add your interpretation. Do NOT say "I was hoping for X."
Just paste the raw output.


### Analyst → Creator (paste back into Creator conversation)

```
[paste the Analyst's full response here]
```

Now you're back in Creator mode. Read the numbers. Interpret.
Decide what's next.


## The full cycle takes about 2 minutes of copy-paste

```
Creator conversation: describe experiment → get script (5-15 min)
  ↓ copy script (10 sec)
Auditor conversation: paste script → get verdict (1-2 min)
  ↓ copy verdict (10 sec)
Creator conversation: fix if needed (0-5 min)
  ↓ save script to Drive
Colab: run 3 cells (experiment runtime)
  ↓ copy Cell 3 output (10 sec)
Analyst conversation: paste output → get report (1 min)
  ↓ copy report (10 sec)
Creator conversation: interpret + plan next (5-15 min)
```

Total copy-paste time: ~40 seconds per experiment cycle.
Total thinking time: as long as you need.
The 40 seconds buys you unbiased code review and unbiased
result reporting. That's the best ROI in research.
