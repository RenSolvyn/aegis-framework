"""
Example: null distribution calibration.
Demonstrates all framework patterns without domain-specific science.
"""

import os, sys, random
import numpy as np

DRIVE_ROOT = os.environ.get("RESEARCH_DRIVE_ROOT", "/content/drive/MyDrive/Research")
sys.path.insert(0, os.path.join(DRIVE_ROOT, "src"))
from research_runner import run_experiment, save_result

SEED = 42
random.seed(SEED)
np.random.seed(SEED)


def experiment(output_dir, program_state):
    random.seed(SEED)
    np.random.seed(SEED)

    n_random = 500
    null_scores = [float(np.random.normal(0, 1)) for _ in range(n_random)]

    percentile_95 = float(np.percentile(null_scores, 95))
    adaptive_threshold = max(percentile_95, 0.05)

    assert np.isfinite(adaptive_threshold)
    assert adaptive_threshold > 0
    assert len(null_scores) == n_random

    save_result(os.path.join(output_dir, "calibration.json"), {
        "n_random": n_random,
        "null_95th": percentile_95,
        "adaptive_threshold": adaptive_threshold,
        "null_mean": float(np.mean(null_scores)),
        "null_std": float(np.std(null_scores)),
    })

    return {
        "state_updates": {
            "calibration.adaptive_threshold": adaptive_threshold,
            "calibration.null_95th_percentile": percentile_95,
        },
        "summary": f"null calibration, threshold={adaptive_threshold:.3f}",
    }


if __name__ == "__main__":
    run_experiment(
        experiment_fn=experiment,
        phase="phase_0",
        work_unit="WU-0.01",
        expected_outputs=["calibration.json"],
    )
