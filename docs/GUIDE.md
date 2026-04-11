# Research Methodology Guide


## The research pipeline

Solo research fails when the same person writes code, evaluates it,
and interprets results without separation. This pipeline creates
separation through infrastructure:

**Aegis AI** — your research assistant. Explores your curiosity,
challenges assumptions, kills bad questions, writes self-audited
experiment scripts, and explains results with devil's advocate
questions. All in one conversation.

**Auditor** (optional, for publication) — reviews the script in
a separate conversation. Checks logic, statistics, seeds, types,
prerequisites. Returns PASS or FAIL. Can't see the hypothesis.

**Cell 3** — the blind layer. Code-generated comparison of
pre-registered predictions vs observed results, plus mechanical
statistical interpretation. Cannot be biased.

**Minimum viable separation:** One AI conversation handles
thinking and execution. The Auditor adds independent review
when publishing. Cell 3 provides the unbiased comparison layer.


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
Errors are auto-logged by the runner when experiments crash.
Anomalies flagged during result review travel through the next
experiment cycle and get embedded as log_error() calls.
You never manually edit the error log.


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
| Conversations | Any AI (Claude, ChatGPT, etc.) | Not artifacts |


## Extending Aegis

Add custom checks without editing framework source. Create
`src/extensions.py` in your project with any of these hooks:

```python
def on_experiment_start(work_unit, phase, program_state):
    """Called before every experiment. Raise to block execution."""
    pass

def on_experiment_end(work_unit, status, results, program_state):
    """Called after every experiment completes."""
    pass

def on_save_result(filepath, data):
    """Called before every result is saved. Raise to block saving."""
    pass

def custom_publication_checks(project_dir):
    """Return list of (name, passed, detail) tuples.
    Added to publication_check() automatically."""
    return []
```

The runner auto-discovers and calls these hooks. If the file doesn't
exist, hooks are silently skipped. If a hook raises an exception,
the runner reports it clearly.
