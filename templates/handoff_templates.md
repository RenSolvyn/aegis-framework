# Handoff Templates

Three roles, three handoffs. Fill the slots, don't improvise the format.


## Creator → Auditor

```
═══ HANDOFF: CREATOR → AUDITOR ═══
Phase: ___  |  Work unit: WU-___

## Script
[the complete script]

## What this does
[2-3 sentences]

## Expected outputs
[files + value ranges]

## Statistical claims
[every threshold, test, comparison]

## Assumptions
[what must be true]

## Uncertainties
[what the Auditor should scrutinize]

## State updates on completion
[dot-path notation, experiment-specific only]

## Error log entries
[from prior Analyst handoff, if any]
═══ END HANDOFF ═══
```


## Auditor → Executor

```
═══ HANDOFF: AUDITOR → EXECUTOR ═══
Phase: ___  |  Work unit: WU-___
Verdict: PASS (iteration ___/3)

## Script
[approved script]

## Findings resolved
[issues found and fixed]

## Error log entries
[Creator entries + Auditor's own catches]
═══ END HANDOFF ═══
```


## Analyst → Creator

```
═══ HANDOFF: ANALYST → CREATOR ═══
Phase: ___  |  Work unit: WU-___

## Results (facts only)
[raw numbers, no interpretation]

## Data integrity: [PASS / FLAG]

## Anomalies
[values outside expected ranges]

## State updates
[feature values, calibration, anomalies]

## Error log entries
[structured entries for anything flagged]
═══ END HANDOFF ═══
```


## Recursion tracker (when Auditor returns FAIL)

```
Iteration 1: FAIL — [issues] — [fix]
Iteration 2: FAIL — [issues] — [fix]
Iteration 3: FAIL → ESCALATE to design review
```


## Error log lifecycle

```
Analyst flags → Creator carries → Auditor adds own →
Executor embeds as log_error() → written BEFORE experiment runs
```
