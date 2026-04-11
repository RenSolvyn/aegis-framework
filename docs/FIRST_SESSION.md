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


### Step 1: One-click setup

Open colab.research.google.com → New notebook. Paste and run:

```python
!pip install -q numpy
import urllib.request
urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/RenSolvyn/aegis-framework/main/examples/colab_setup.py",
    "setup.py")
exec(open("setup.py").read())
```

This creates the entire project on Google Drive, downloads the
framework from GitHub, and runs a smoke test. When you see
"Setup complete" — you're ready.


### Step 2: Every future session

Copy the 3 cells from `examples/colab_notebook.py` into a Colab
notebook, or just open **Aegis_Research_Session.ipynb** from your
Drive (the setup created it automatically — double-click to open
in Colab):

- **Cell 1** — mounts Drive, shows dashboard, finds your scripts.
  First time? Auto-creates the project. Returning? Shows where you
  left off. You never change this cell.

- **Cell 2** — automatically finds and runs the newest script in
  your `scripts/` folder. No filename to type. You never change
  this cell either.

- **Cell 3** — shows your results formatted with clear "copy from
  here" and "stop copying here" markers. Includes pre-registered
  predictions, observed results, and blind interpretation
  (code-generated). Copy everything between the markers and paste
  it to your Pipeline AI.

That's it. Three cells, never edited. Your only job is pasting
scripts into Cell 2 and interpreting results.


---


## Using AI assistants

### Brainstorming (Brainstorm AI)
Open your Research Brainstorm project and just talk:

> I wonder if coffee makes plants grow faster. Can I test that?

The AI explores the idea with you, challenges your assumptions,
and produces a RESEARCH PLAN when the question is ready.

### Running experiments (Pipeline AI)
Paste the RESEARCH PLAN and the AI writes the script. After
running it in Colab, paste the Cell 3 results back:

> Analyze these results.

The AI explains every number in plain English and asks devil's
advocate questions. You decide what it means.

### Reviewing scripts (Auditor — optional, for publication)
In a **separate conversation**, paste the script and say:

> Audit this script. Check: logic errors, seeds, type casting,
> prerequisites, calibration. PASS or FAIL with findings.


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
