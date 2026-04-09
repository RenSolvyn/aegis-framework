# ================================================================
# CELL 1: SESSION START (same every time — just run it)
# ================================================================

from google.colab import drive
drive.mount('/content/drive')

import sys
sys.path.insert(0, "/content/drive/MyDrive/Research/src")

# Show dashboard — tells you where you are and what's next
from research_runner import dashboard
state = dashboard()

# Setup git (auto-pulls latest)
from git_sync import git_setup
git_setup()


# ================================================================
# CELL 2: YOUR EXPERIMENT (the only cell you change)
# ================================================================

# Option A: run a script file
!python /content/drive/MyDrive/Research/scripts/wu_pg04_l1_probes.py

# Option B: paste experiment code directly (for quick tests)
# from research_runner import run_experiment, save_result
# def experiment(output_dir, program_state):
#     ...
# run_experiment(experiment_fn=experiment, phase="...", work_unit="...",
#                expected_outputs=["..."])


# ================================================================
# CELL 3: SESSION END (same every time — just run it)
#
# NOTE: If you integrated git_sync into the runner (recommended),
# this cell is unnecessary — the runner auto-syncs.
# Keep it as a fallback or for manual sync.
# ================================================================

from git_sync import git_sync
import json

state = json.load(open("/content/drive/MyDrive/Research/program_state.json"))
git_sync(
    work_unit=state.get("last_work_unit", "unknown"),
    phase="pre_gate",  # change to match your current phase
    status=state.get("last_session_status", "COMPLETE"),
    runtime_hours=0,
    summary=""  # one-line result summary
)
