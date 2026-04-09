# Your First Session with Aegis

You found this repo. You're a solo researcher. You want to use it.
Here's exactly what to do, from zero to your first tracked experiment.

**Total time: ~30 minutes.**


## Step 1: Get the code (2 min)

### Option A: Clone with git
```bash
git clone https://github.com/RenSolvyn/aegis-framework.git
cd aegis-framework
```

### Option B: Download the zip
Click the green "Code" button on GitHub → Download ZIP → unzip it.


## Step 2: Bootstrap your project (1 min)

Open your terminal. Run:

```bash
python bootstrap.py my-research "My Research Program" 100
```

Replace:
- `my-research` → your project folder name
- `"My Research Program"` → what you're studying
- `100` → your total GPU budget in hours

The bootstrap:
- Creates the folder structure
- Copies the runner and git_sync
- Initializes program_state.json with your budget
- Runs a smoke test to verify everything works
- Prints the dashboard showing Session 1

You should see:
```
======================================================
  Aegis Session 1
  Phase: phase_0
  Last: None → None
  Budget: 0.0 / 100 hrs (0.0% spent)
  Remaining: 100.0 hrs
  Anomalies: none
======================================================
```

If you see that, everything works. Move on.


## Step 3: Define your research (15 min, no code)

Before writing any experiment, answer these questions in a file
called `docs/research_plan.md` in your project:

```markdown
# Research Plan

## Question
What am I trying to find out?

## Phases
What are the major stages of this research?
(Example: calibration → main experiment → validation → analysis)

## Work units
What are the individual tasks within each phase?
List them. Note which ones depend on which.

## Kill criteria
Under what conditions do I stop or pivot?
(Example: if accuracy < 0.5 on the calibration set, the method doesn't work)

## Budget
How many GPU hours total? How many per phase?

## Negative-result plan
If the main hypothesis fails, what do I produce instead?
```

This file is for YOU. It forces you to think before you code.
Commit it to your project repo.


## Step 4: Write your first experiment (10 min)

Copy the template:
```bash
cd my-research
cp ../aegis-framework/templates/script_template.py scripts/wu_0_01_my_first_experiment.py
```

Open it in any editor. The template has all the patterns baked in —
seeds, prerequisites, save_result, state_updates. Replace the
placeholder comments with your actual science.

Here's the minimum viable experiment:

```python
import os, sys, random
import numpy as np

DRIVE_ROOT = os.environ.get("RESEARCH_DRIVE_ROOT", ".")
sys.path.insert(0, os.path.join(DRIVE_ROOT, "src"))
from research_runner import run_experiment, save_result

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

def experiment(output_dir, program_state):
    random.seed(SEED)
    np.random.seed(SEED)

    # === YOUR SCIENCE HERE ===
    # Replace this with your actual experiment
    data = np.random.randn(1000)
    mean = float(np.mean(data))
    std = float(np.std(data))

    results = {"mean": mean, "std": std, "n": 1000}

    assert np.isfinite(mean), "Mean is not finite"

    save_result(os.path.join(output_dir, "results.json"), dict(results))

    return {
        "state_updates": {"calibration.baseline_mean": mean},
        "summary": f"baseline computed, mean={mean:.3f}",
    }

if __name__ == "__main__":
    run_experiment(
        experiment_fn=experiment,
        phase="phase_0",
        work_unit="WU-0.01",
        expected_outputs=["results.json"],
    )
```

## Step 5: Run it (1 min)

### Locally:
```bash
cd my-research
RESEARCH_DRIVE_ROOT=. python scripts/wu_0_01_my_first_experiment.py
```

### On Colab:
Upload `src/` and `program_state.json` to Google Drive.
Use the 3-cell template from `examples/colab_3cell_template.py`.

The runner prints your session number, output directory, runtime,
and budget — all automatic.


## Step 6: Check what happened (1 min)

```bash
# See the dashboard
RESEARCH_DRIVE_ROOT=. python -c "
import sys; sys.path.insert(0, 'src')
from research_runner import dashboard
dashboard()
"
```

You should see Session 2, your work unit marked COMPLETE, and your
budget updated.

Check the output:
```bash
cat results/phase_0/*/results.json
```


## What's next

You now have a working research pipeline. Every experiment you run
from here is:
- Session-tracked (numbered, timed, budget-aware)
- Output-verified (SHA-256 checksums)
- State-managed (program_state.json updated atomically)
- Crash-safe (errors auto-logged, partial state preserved)

To add the 3-role pipeline (Creator/Auditor/Analyst), read
`docs/GUIDE.md` and use the handoff templates in `templates/`.

To add version control, read `docs/SETUP.md`.

To add auto-commit from Colab, see the git_sync section in
`docs/SETUP.md`.


## Using AI assistants with Aegis

If you use Claude, ChatGPT, or another AI assistant to help write
experiment scripts, here's how to set it up:

### Project setup (Claude)
Create a Claude Project. Add these as project files:
- `docs/GUIDE.md` (so it knows the conventions)
- `templates/handoff_templates.md` (so it uses the handoff format)
- `templates/script_template.py` (so scripts follow the pattern)

### Your first prompt
Paste your `program_state.json` and say:

```
Here's my program state. I'm working on [phase/work unit].
I need an experiment script that [what it should do].

The script should:
- Follow the Aegis script conventions
- Load any calibration values from program_state (never hardcode)
- Include runtime assertions on intermediate values
- End with a HANDOFF block for the Auditor

Here's my research context: [brief description]
```

### For the Auditor role
Start a separate conversation. Paste the script and say:

```
Please audit this experiment script. Check for:
- Logic errors and edge cases
- Statistical mistakes (wrong test, wrong threshold)
- Seed discipline (random, numpy, torch all seeded?)
- Type safety (explicit float/int/bool casting?)
- Prerequisites (correct work units checked?)
- Calibration (loaded from state, not hardcoded?)

Return PASS or FAIL with specific findings.
```

### For the Analyst role
After running on Colab, bring the output and say:

```
Here are the outputs from WU-0.01. Report facts only:
- Data integrity (files present, NaN/Inf check)
- Raw statistical numbers
- Anything outside expected ranges
- Do NOT interpret what it means — just report the numbers.
```

The separation between roles is the structure. The AI helps you
play each role more effectively, but the context switch between
conversations is what prevents your assumptions from leaking.
