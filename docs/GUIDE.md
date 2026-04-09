# Research Methodology Guide


## The 3-role pipeline

Solo research fails when the same person writes code, evaluates it,
and interprets results without separation. This pipeline forces
context switches between three roles:

**Creator** — writes the experiment script + structured handoff.
Documents assumptions AND uncertainties. Produces the science.

**Auditor** — reviews the script with fresh eyes. Checks logic,
statistics, seeds, types, prerequisites. Returns PASS or FAIL.
Max 3 iterations, then escalate to design review.

**Analyst** — receives Colab output. Reports facts only: accuracy
= 0.87, p = 0.003, BF = 14.2. No interpretation. That happens
when the handoff returns to the Creator.

The Executor role (wrapping scripts for Colab) merges into the
Auditor — it's mechanical and doesn't need a separate session.

**Minimum viable separation:** Write the script in one sitting.
Take a break (even 10 minutes). Review it in a separate sitting.
The break is the load-bearing structure, not the role names.


## Script conventions

**Seeds everywhere.** Module level AND inside experiment().
random, numpy, torch, cuda. Miss one → not reproducible.

**Calibration from state, never hardcoded.**
```python
threshold = program_state["calibration"]["adaptive_threshold"]
assert threshold is not None, "Run calibration first"
```

**Explicit type casting.** No numpy types in JSON:
```python
results["mean"] = float(np.mean(values))
results["pass"] = bool(float(p) < 0.05)
```

**save_result() mutates its input.** Pass `dict(data)` if you
iterate afterward.

**Prerequisites checked at the top.**
```python
assert program_state["phases"]["phase_0"]["work_units"].get("WU-0.01") == "COMPLETE"
```

**Work unit status is auto-managed.** Never include it in
state_updates — the runner handles it.

**Error log entries at the top of experiment(), before any code.**
They execute first, so even if the experiment crashes, prior
findings are logged.


## Design patterns

### Negative-result architecture
Before starting, map every outcome to a product:

| Outcome | Product |
|---------|---------|
| Strong positive | Your ideal product |
| Weak positive | Simplified version |
| Negative with evidence | Methodology paper + tools |
| Inconclusive | Dataset + framework release |

Design the negative-result product BEFORE seeing data.

### Kill criteria
Non-negotiable stopping rules with evidence thresholds:

| Condition | Evidence | Action |
|-----------|----------|--------|
| Gate fails | BF > 10 against | Pivot |
| Main result null | BF > 10 against | Skip to fallback |
| Product below bar | Metric < floor | Negative paper |
| Budget > 90% | Arithmetic | Invoke triage |

Written in present tense. Not suggestions.

### Calibration-before-measurement
Generate a null distribution from your setup before running real
experiments. Derive thresholds from the null, not from theory.
Then run the real experiment.

### Triage protocol
Pre-classify work units before the program starts:
- **A** (never cut): data consumed by downstream phases
- **B** (cut if needed): strengthens claims but not required
- **C** (cut first): nice-to-have, no downstream dependency

Classify when you're NOT under pressure.

### Session rhythm
- Hard time limit per session (e.g., 7 hours)
- Bug: 30-minute time box. Not solved → log it, move on.
- Design question: 0 minutes in-session. Solve between sessions.
- Mandatory break between phases (1+ days)

### Error log lifecycle
Entries ride the handoff chain: Analyst flags → Creator carries →
Auditor adds → Executor embeds as log_error() → written to Drive
BEFORE experiment runs. You never manually edit the error log.


## What lives where

| Content | Location | Why |
|---------|----------|-----|
| Approved scripts | Git repo | Version control |
| program_state.json | Drive + Git | Drive=runtime, Git=history |
| Result summaries | Git repo | Audit trail |
| Raw outputs | Drive only | Large files |
| Probe weights (.pt) | Drive only | Binary, large |
| Model checkpoints | Drive only | Very large |
| error_log.md | Drive only | Append-only |
| Conversations | Claude Projects | Not artifacts |
