#!/usr/bin/env python3
"""
Aegis Bootstrap — set up a new research project in one command.

Usage:
    python bootstrap.py my-project "My Research Program" 100

    Arguments:
        project_name    Folder name for your project
        program_name    Human-readable name (in quotes)
        budget_hours    Total GPU hours budgeted

Creates the project structure, initializes program_state.json,
copies the runner, and runs a smoke test to verify everything works.
"""

import os
import sys
import json
import shutil
from datetime import datetime, timezone


def main():
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python bootstrap.py <project_name> [program_name] [budget_hours]")
        print()
        print("Example:")
        print('  python bootstrap.py my-research "Attention Study" 200')
        print()
        print("This creates a ready-to-use research project folder.")
        sys.exit(1)

    project_name = sys.argv[1]
    program_name = sys.argv[2] if len(sys.argv) > 2 else project_name
    budget_hours = int(sys.argv[3]) if len(sys.argv) > 3 else 100

    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.join(os.getcwd(), project_name)

    if os.path.exists(project_dir):
        print(f"[bootstrap] ERROR: {project_dir} already exists.")
        sys.exit(1)

    print(f"[bootstrap] Creating project: {program_name}")
    print(f"[bootstrap] Location: {project_dir}")
    print(f"[bootstrap] Budget: {budget_hours} hours")
    print()

    # Create directory structure
    dirs = [
        "src",
        "scripts",
        "results/summaries",
        "data",
        "logs",
        "docs",
    ]
    for d in dirs:
        os.makedirs(os.path.join(project_dir, d), exist_ok=True)
        print(f"  Created {d}/")

    # Copy runner
    runner_src = os.path.join(script_dir, "src", "research_runner.py")
    runner_dst = os.path.join(project_dir, "src", "research_runner.py")
    if os.path.exists(runner_src):
        shutil.copy2(runner_src, runner_dst)
        print(f"  Copied research_runner.py")
    else:
        print(f"  WARNING: research_runner.py not found at {runner_src}")

    # Copy git_sync
    sync_src = os.path.join(script_dir, "src", "git_sync.py")
    sync_dst = os.path.join(project_dir, "src", "git_sync.py")
    if os.path.exists(sync_src):
        shutil.copy2(sync_src, sync_dst)
        print(f"  Copied git_sync.py")

    # Create program_state.json
    state = {
        "program": {
            "name": program_name,
            "version": "v1",
            "created": datetime.now(timezone.utc).isoformat(),
            "framework": "aegis-v2",
        },
        "last_session": 0,
        "last_session_status": None,
        "last_work_unit": None,
        "last_modified": None,
        "budget": {
            "total_hours": budget_hours,
            "spent_hours": 0,
            "remaining_hours": budget_hours,
        },
        "calibration": {},
        "features": {},
        "anomalies": [],
        "phases": {
            "phase_0": {
                "status": "NOT_STARTED",
                "hours_spent": 0,
                "work_units": {},
            },
        },
    }
    state_path = os.path.join(project_dir, "program_state.json")
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)
    print(f"  Created program_state.json (budget: {budget_hours} hrs)")

    # Create .gitignore
    gitignore = """*.pt
*.npz
*.bin
*.safetensors
models/
results/raw/
__pycache__/
*.pyc
.env
.DS_Store
*.tmp
"""
    with open(os.path.join(project_dir, ".gitignore"), "w") as f:
        f.write(gitignore)
    print(f"  Created .gitignore")

    # Create error log
    with open(os.path.join(project_dir, "logs", "error_log.md"), "w") as f:
        f.write(f"# Error Log — {program_name}\n\nEntries are appended by the Aegis runner.\n")
    print(f"  Created logs/error_log.md")

    # Run smoke test
    print()
    print("[bootstrap] Running smoke test...")
    print()

    # Temporarily set DRIVE_ROOT to project_dir for the test
    os.environ["RESEARCH_DRIVE_ROOT"] = project_dir
    sys.path.insert(0, os.path.join(project_dir, "src"))

    # Reimport with new path
    import importlib
    if "research_runner" in sys.modules:
        del sys.modules["research_runner"]

    from research_runner import run_experiment, save_result, dashboard

    # Show dashboard
    state = dashboard(state_path)

    # Run a trivial experiment
    def smoke_test(output_dir, program_state):
        results = {
            "test": "smoke",
            "status": "passed",
            "framework_version": "aegis-v2",
        }
        save_result(os.path.join(output_dir, "smoke_test.json"), dict(results))
        return {
            "state_updates": {},
            "summary": "bootstrap smoke test passed",
        }

    status = run_experiment(
        experiment_fn=smoke_test,
        phase="phase_0",
        work_unit="WU-SMOKE",
        expected_outputs=["smoke_test.json"],
    )

    print()
    if status == "COMPLETE":
        print("=" * 54)
        print("  Aegis bootstrap COMPLETE")
        print(f"  Project: {project_dir}")
        print()
        print("  Next steps:")
        print("    1. cd " + project_name)
        print("    2. Write your first real experiment")
        print("    3. python src/your_script.py")
        print()
        print("  For Colab: copy src/ and program_state.json")
        print("  to Google Drive, use the 3-cell template.")
        print()
        print("  For git: git init && git add . && git commit")
        print("=" * 54)
    else:
        print(f"  Smoke test FAILED with status: {status}")
        print("  Check the output above for errors.")

    return status


if __name__ == "__main__":
    main()
