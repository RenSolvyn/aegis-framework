"""
Experiment script template.
File naming: wu_{phase}{number}_{description}.py
"""

import os, sys, json, random
import numpy as np

DRIVE_ROOT = "/content/drive/MyDrive/Research"
sys.path.insert(0, os.path.join(DRIVE_ROOT, "src"))
from research_runner import run_experiment, save_result, log_error

SEED = 42
random.seed(SEED)
np.random.seed(SEED)


def experiment(output_dir, program_state):
    # --- Error log entries from prior handoff ---
    # log_error("WU-X.XX", "Auditor", "BUG — ...", "...",
    #           resolution="Fixed", lesson="...")
    # --- End error log entries ---

    # Prerequisites
    # assert program_state["phases"]["phase_0"]["work_units"].get("WU-0.01") == "COMPLETE"

    # Load calibration from state (NEVER hardcode)
    # threshold = program_state["calibration"]["adaptive_threshold"]

    random.seed(SEED)
    np.random.seed(SEED)

    # === Your science here ===

    results = {}

    # Runtime assertions
    # assert 0 <= results["accuracy"] <= 1

    # Save (pass dict() to avoid _metadata mutation issue)
    save_result(os.path.join(output_dir, "results.json"), dict(results))

    return {
        "state_updates": {},
        "summary": "one-line description for git commit",
    }


if __name__ == "__main__":
    run_experiment(
        experiment_fn=experiment,
        phase="phase_0",
        work_unit="WU-0.01",
        expected_outputs=["results.json"],
    )
