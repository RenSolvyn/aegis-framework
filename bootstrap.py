#!/usr/bin/env python3
"""
Aegis Bootstrap — set up a new research project in one command.

Usage:
    python3 bootstrap.py my-project "My Research Program" 100

Creates project structure, validates prerequisites, copies all modules,
initializes state, and runs a smoke test.
"""

import os
import sys
import json
import shutil
from datetime import datetime, timezone


def check_prerequisites():
    """Verify Python version and required packages."""
    issues = []

    # Python version
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 8):
        issues.append(
            f"Python 3.8+ required, you have {v.major}.{v.minor}.\n"
            "  Install from python.org or your package manager."
        )

    # numpy
    try:
        import numpy
    except ImportError:
        issues.append(
            "numpy is required but not installed.\n"
            "  Fix: pip3 install numpy"
        )

    if issues:
        print()
        print("  Prerequisites not met:")
        for issue in issues:
            print(f"    - {issue}")
        print()
        return False

    return True


def main():
    if len(sys.argv) < 2:
        print()
        print("  Aegis — create a new research project")
        print()
        print("  Usage:")
        print('    python3 bootstrap.py my-project "My Study" 100')
        print()
        print("  Arguments:")
        print("    my-project    Folder name (no spaces)")
        print('    "My Study"    Your research program name')
        print("    100           Total compute hours budgeted")
        print()
        sys.exit(1)

    project_name = sys.argv[1]
    program_name = sys.argv[2] if len(sys.argv) > 2 else project_name
    budget_hours = int(sys.argv[3]) if len(sys.argv) > 3 else 100

    # Validate
    if not check_prerequisites():
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.join(os.getcwd(), project_name)

    if os.path.exists(project_dir):
        print(f"\n  Folder '{project_name}' already exists. Choose a different name.\n")
        sys.exit(1)

    print()
    print(f"  Creating: {program_name}")
    print(f"  Location: {project_dir}")
    print(f"  Budget:   {budget_hours} hours")
    print()

    # Create directories
    for d in ["src", "scripts", "results/summaries", "data", "logs", "docs"]:
        os.makedirs(os.path.join(project_dir, d), exist_ok=True)
        print(f"    Created {d}/")

    # Copy all source modules
    src_files = ["research_runner.py", "scientific_method.py", "git_sync.py", "config.py", "extensions.py"]
    for filename in src_files:
        src = os.path.join(script_dir, "src", filename)
        dst = os.path.join(project_dir, "src", filename)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"    Copied {filename}")
        else:
            if filename in ("research_runner.py",):
                print(f"    WARNING: {filename} not found — framework may not work")
            else:
                print(f"    Skipped {filename} (optional)")

    # Create program_state.json
    state = {
        "program": {
            "name": program_name,
            "version": "v1",
            "created": datetime.now(timezone.utc).isoformat(),
            "framework": "aegis-v4.0",
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
    print(f"    Created program_state.json")

    # Create .gitignore
    with open(os.path.join(project_dir, ".gitignore"), "w") as f:
        f.write("*.pt\n*.npz\n*.bin\n*.safetensors\nmodels/\n"
                "results/raw/\n__pycache__/\n*.pyc\n.env\n.DS_Store\n*.tmp\n")
    print(f"    Created .gitignore")

    # Create error log
    with open(os.path.join(project_dir, "logs", "error_log.md"), "w") as f:
        f.write(f"# Error Log — {program_name}\n\n"
                "Entries are appended automatically by the Aegis runner.\n")
    print(f"    Created error log")

    # Smoke test
    print()
    print("  Running smoke test...")
    print()

    os.environ["RESEARCH_DRIVE_ROOT"] = project_dir
    sys.path.insert(0, os.path.join(project_dir, "src"))

    import importlib
    for mod in ["config", "research_runner"]:
        if mod in sys.modules:
            del sys.modules[mod]

    from research_runner import run_experiment, save_result, dashboard

    state_result = dashboard(state_path)

    def smoke_test(output_dir, program_state):
        results = {"test": "smoke", "status": "passed"}
        save_result(os.path.join(output_dir, "smoke_test.json"), dict(results))
        return {"state_updates": {}, "summary": "smoke test passed"}

    status = run_experiment(
        experiment_fn=smoke_test,
        phase="phase_0",
        work_unit="WU-SMOKE",
        expected_outputs=["smoke_test.json"],
        rigor="explore",
    )

    if status == "COMPLETE":
        print("  ╔══════════════════════════════════════════╗")
        print("  ║  Aegis project created successfully      ║")
        print("  ╚══════════════════════════════════════════╝")
        print()
        print("  What to do next:")
        print()
        print(f"    cd {project_name}")
        print()
        print("  Then either:")
        print("    a) Write your research plan in docs/research_plan.md")
        print("    b) Ask an AI to write your first experiment")
        print('       (paste the creator_prompt.md and say what you want to study)')
        print("    c) Copy src/ + program_state.json to Google Drive for Colab")
        print()
    else:
        print(f"\n  Smoke test failed ({status}). Check output above.\n")

    return status


if __name__ == "__main__":
    main()
