# Your First Session with Aegis

A complete guide from "I just found this repo" to "my first tracked
experiment." Assumes nothing — if you've never used a terminal, start
at the top.

**Total time: 20-30 minutes.**


## Prerequisites checklist

Before starting, verify you have these:

### Python (required)
Open a terminal and type:
```bash
python3 --version
```
If you see `Python 3.8` or higher, you're good. If "command not found":
- **Mac:** install from python.org or `brew install python3`
- **Linux:** `sudo apt install python3`
- **Windows:** Download from python.org, check "Add to PATH" during install
- **None of these work?** Skip local setup — go to "Colab-first path" below

### How to open a terminal
- **Mac:** Cmd+Space, type "Terminal", Enter
- **Linux:** Ctrl+Alt+T
- **Windows:** Win key, type "PowerShell", Enter
- **Chromebook:** Use Colab-first path instead

### A text editor
VS Code (free, code.visualstudio.com), Sublime Text, or any editor that can save `.py` files.


## Choose your path

**Path A: Local** — you have Python on your computer → follow Steps 1-6

**Path B: Colab-first** — you only use Google Colab → skip to "Colab-first path" below


---

## Path A: Local setup


### Step 1: Get the code (1 min)

**With git:**
```bash
git clone https://github.com/RenSolvyn/aegis-framework.git
cd aegis-framework
```

**Without git (download zip):**
1. Go to github.com/RenSolvyn/aegis-framework
2. Click green **Code** button → **Download ZIP**
3. Unzip it, open terminal, navigate to the folder


### Step 2: Bootstrap your project (1 min)

```bash
python3 bootstrap.py my-research "My Research Program" 100
```

Arguments:
- `my-research` → folder name (no spaces, lowercase)
- `"My Research Program"` → your program's name
- `100` → total GPU hours budgeted

You should see the dashboard and "Aegis bootstrap COMPLETE."

**Troubleshooting:**
- `command not found` → try `python` instead of `python3`
- `No module named numpy` → run `pip3 install numpy` first
- `Permission denied` → make sure you're in the right folder


### Step 3: Plan your research (10 min, no code)

Create `my-research/docs/research_plan.md` in your text editor:

```markdown
# Research Plan

## Question
What am I trying to find out?

## Phases
- phase_0: Calibration
- phase_1: Main experiment
- phase_2: Validation

## Work units (tasks within each phase)
- WU-0.01: Generate null distribution
- WU-0.02: Calibrate thresholds
- WU-1.01: Run main experiment
(list all tasks, note dependencies)

## Kill criteria
- Calibration accuracy < 50%: method doesn't work, pivot
- Budget > 90% spent: invoke triage

## If the hypothesis fails, I still produce:
- The dataset
- The measurement tool
- A paper about what didn't work
```


### Step 4: Write your first experiment

Create `my-research/scripts/wu_0_01_baseline.py`:

```python
import os, sys, random
import numpy as np

DRIVE_ROOT = os.environ.get("RESEARCH_DRIVE_ROOT",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(DRIVE_ROOT, "src"))
from research_runner import run_experiment, save_result

SEED = 42
random.seed(SEED)
np.random.seed(SEED)


def experiment(output_dir, program_state):
    random.seed(SEED)
    np.random.seed(SEED)

    # ========== YOUR SCIENCE HERE ==========
    data = np.random.randn(1000)
    results = {
        "mean": float(np.mean(data)),
        "std": float(np.std(data)),
        "n_samples": 1000,
    }

    # Sanity checks
    assert np.isfinite(results["mean"]), "Mean is NaN or Inf"

    # Save (always use dict() to avoid mutation bug)
    save_result(os.path.join(output_dir, "baseline.json"), dict(results))

    return {
        "state_updates": {
            "calibration.baseline_mean": results["mean"],
        },
        "summary": f"baseline: mean={results['mean']:.3f}",
    }


if __name__ == "__main__":
    run_experiment(
        experiment_fn=experiment,
        phase="phase_0",
        work_unit="WU-0.01",
        expected_outputs=["baseline.json"],
    )
```


### Step 5: Run it

```bash
cd my-research
python3 scripts/wu_0_01_baseline.py
```

You should see the runner print session number, output path, status
COMPLETE, and budget.


### Step 6: Check the dashboard

```bash
python3 -c "import sys,os;os.environ['RESEARCH_DRIVE_ROOT']='.';sys.path.insert(0,'src');from research_runner import dashboard;dashboard()"
```

You should see your session count, budget, and last work unit.

**You're done. You're running tracked experiments.**


---


## Colab-first path (no local Python needed)


### Step 1: Download the repo

Go to github.com/RenSolvyn/aegis-framework → Code → Download ZIP. Unzip.


### Step 2: Upload to Google Drive

In Google Drive, create a folder called `Research`. Upload:
```
Research/
├── src/
│   ├── research_runner.py     (from zip src/ folder)
│   └── git_sync.py            (from zip src/ folder)
└── program_state.json         (copy templates/program_state_template.json,
                                rename it, edit your name and budget)
```


### Step 3: Open Colab and run

Go to colab.research.google.com → New notebook.

**Cell 1 — Setup (same every session):**
```python
from google.colab import drive
drive.mount('/content/drive')

import os, sys
os.environ["RESEARCH_DRIVE_ROOT"] = "/content/drive/MyDrive/Research"
sys.path.insert(0, "/content/drive/MyDrive/Research/src")
from research_runner import dashboard
dashboard()
```

**Cell 2 — Your experiment (change this each time):**
```python
from research_runner import run_experiment, save_result
import numpy as np, random, os

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

def experiment(output_dir, program_state):
    random.seed(SEED)
    np.random.seed(SEED)

    # YOUR SCIENCE HERE
    data = np.random.randn(1000)
    results = {"mean": float(np.mean(data)), "std": float(np.std(data))}
    save_result(os.path.join(output_dir, "results.json"), dict(results))
    return {"state_updates": {"calibration.mean": results["mean"]}}

run_experiment(experiment_fn=experiment, phase="phase_0",
               work_unit="WU-0.01", expected_outputs=["results.json"])
```

**Cell 3 — Dashboard (verify it worked):**
```python
dashboard()
```

Results are on Drive. State is updated. Close Colab. Done.


---


## Using AI assistants

### Writing scripts (Creator role)
Paste `program_state.json` and say:

> I need a script for WU-0.01 that [does X]. Follow Aegis conventions:
> seeds, calibration from state, save_result with dict(), assertions.

### Reviewing scripts (Auditor role — separate conversation)
Paste the script and say:

> Audit this script. Check: logic errors, seeds, type casting,
> prerequisites, calibration. PASS or FAIL with findings.

### Reading results (Analyst role — separate conversation)
Paste the output and say:

> Report facts only: data integrity, raw numbers, anomalies.
> Do NOT interpret.

Use **separate conversations** for each role. The context switch
is the structure.


---


## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python3: command not found` | Try `python`. Or install from python.org |
| `No module named research_runner` | Check RESEARCH_DRIVE_ROOT points to your project |
| `No module named numpy` | `pip3 install numpy` (local) or `!pip install numpy` (Colab) |
| `program_state.json not found` | Set RESEARCH_DRIVE_ROOT environment variable |
| Dashboard shows wrong session | Smoke test = session 1. Your first real experiment = session 2 |
| `Git sync skipped` | Normal — git isn't configured. Experiment still works |
| Colab disconnected mid-run | Reconnect. Check error_log.md. Rerun the experiment |
| Results folder is empty | Check the path runner printed — results are in timestamped subdirs |
