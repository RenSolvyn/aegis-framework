"""
Experiment script template.
File naming: wu_{phase}{number}_{description}.py

The AI Creator produces scripts like this. You shouldn't need to
edit this manually — describe what you want to measure and the AI
writes it for you.
"""

import os, sys, random
import numpy as np

DRIVE_ROOT = os.environ.get("RESEARCH_DRIVE_ROOT",
    "/content/drive/MyDrive/Research")
sys.path.insert(0, os.path.join(DRIVE_ROOT, "src"))
from research_runner import run_experiment, save_result
from scientific_method import pre_register

SEED = 42
random.seed(SEED)
np.random.seed(SEED)


def experiment(output_dir, program_state):
    random.seed(SEED)
    np.random.seed(SEED)

    # Lock predictions BEFORE any computation
    pre_register(output_dir,
        predictions={
            "hypothesis": "FILL IN: what you believe",
            "prediction": "FILL IN: measurable outcome you expect",
            "null_prediction": "FILL IN: what you'd see if wrong",
            "what_would_change_my_mind": "FILL IN: strongest disconfirmation"
        },
        analysis_plan={
            "data_cleaning": "FILL IN: how you handle outliers/missing data",
            "statistical_test": "FILL IN: which test and why",
            "exclusion_criteria": "FILL IN: what data gets excluded",
            "multiple_comparisons": "FILL IN: correction if >1 test",
            "sample_size_justification": "FILL IN: why N is sufficient"
        }
    )

    # YOUR EXPERIMENT HERE
    results = {
        "value": float(0.0),
    }

    # Sanity checks
    assert np.isfinite(results["value"]), "Result is NaN or Inf"

    # Save (always use dict() to avoid mutation bug)
    save_result(os.path.join(output_dir, "results.json"), dict(results))

    return {
        "state_updates": {},
        "summary": "one-line summary of what happened",
    }


if __name__ == "__main__":
    run_experiment(
        experiment_fn=experiment,
        phase="phase_0",
        work_unit="WU-0.01",
        expected_outputs=["results.json"],
    )
