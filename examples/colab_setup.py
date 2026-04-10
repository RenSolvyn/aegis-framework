"""
Aegis Colab Setup — run once to create your research project on Google Drive.

In a Colab notebook, run this single cell:

    !pip install -q numpy
    exec(open("/content/drive/MyDrive/aegis-setup.py").read())

Or paste this entire file into a Colab cell and run it.

It creates the full project structure on Drive, copies the framework
files, initializes program_state.json, and runs a smoke test.
After this, every future session uses the 3-cell template.
"""

import os
import sys
import json
import shutil
from datetime import datetime, timezone


# =====================================================================
# CONFIGURATION — change these to match your research
# =====================================================================

PROGRAM_NAME = "My Research Program"   # Change this to your program name
BUDGET_HOURS = 100                     # Change this to your compute budget
PROJECT_FOLDER = "Research"            # Folder name on Google Drive

# =====================================================================
# Don't edit below this line
# =====================================================================

def setup():
    # Mount Drive
    try:
        from google.colab import drive
        drive.mount('/content/drive')
    except ImportError:
        print("  This script is designed for Google Colab.")
        print("  For local setup, use bootstrap.py instead.")
        return False

    DRIVE_ROOT = f"/content/drive/MyDrive/{PROJECT_FOLDER}"
    os.environ["RESEARCH_DRIVE_ROOT"] = DRIVE_ROOT

    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║  Aegis — Setting up your research        ║")
    print("  ╚══════════════════════════════════════════╝")
    print()
    print(f"  Program: {PROGRAM_NAME}")
    print(f"  Location: Google Drive/{PROJECT_FOLDER}/")
    print(f"  Budget: {BUDGET_HOURS} hours")
    print()

    # Create directory structure
    dirs = [
        "src",
        "scripts",
        "results",
        "data",
        "logs",
        "docs",
    ]

    for d in dirs:
        path = os.path.join(DRIVE_ROOT, d)
        os.makedirs(path, exist_ok=True)
        if not os.listdir(path) if os.path.isdir(path) else True:
            print(f"    Created {d}/")
        else:
            print(f"    {d}/ (already exists)")

    # Write framework source files directly
    # (no need to upload — we create them here)

    # --- config.py ---
    config_content = '''"""Aegis Configuration"""
import os
DRIVE_ROOT = os.environ.get("RESEARCH_DRIVE_ROOT", "/content/drive/MyDrive/''' + PROJECT_FOLDER + '''")
STATE_FILE = os.path.join(DRIVE_ROOT, "program_state.json")
ERROR_LOG = os.path.join(DRIVE_ROOT, "logs", "error_log.md")
RESULTS_ROOT = os.path.join(DRIVE_ROOT, "results")
SCRIPTS_DIR = os.path.join(DRIVE_ROOT, "scripts")
SRC_DIR = os.path.join(DRIVE_ROOT, "src")
VERSION = "3.1.0"
'''
    _write_if_new(os.path.join(DRIVE_ROOT, "src", "config.py"), config_content)

    # --- research_runner.py (minimal inline version for bootstrapping) ---
    # Check if full runner already exists
    runner_path = os.path.join(DRIVE_ROOT, "src", "research_runner.py")
    if not os.path.exists(runner_path):
        print()
        print("  NOTE: research_runner.py not found on Drive.")
        print("  Downloading from GitHub...")
        try:
            import urllib.request
            url = "https://raw.githubusercontent.com/RenSolvyn/aegis-framework/main/src/research_runner.py"
            urllib.request.urlretrieve(url, runner_path)
            print("    Downloaded research_runner.py")
        except Exception as e:
            print(f"    Could not download: {e}")
            print("    Manually upload research_runner.py to Drive/{}/src/".format(PROJECT_FOLDER))
            return False
    else:
        print(f"    research_runner.py (already exists)")

    # Download scientific_method.py if missing
    sm_path = os.path.join(DRIVE_ROOT, "src", "scientific_method.py")
    if not os.path.exists(sm_path):
        try:
            import urllib.request
            url = "https://raw.githubusercontent.com/RenSolvyn/aegis-framework/main/src/scientific_method.py"
            urllib.request.urlretrieve(url, sm_path)
            print("    Downloaded scientific_method.py")
        except Exception:
            print("    Skipped scientific_method.py (optional, download later)")
    else:
        print(f"    scientific_method.py (already exists)")

    # Download git_sync.py if missing
    gs_path = os.path.join(DRIVE_ROOT, "src", "git_sync.py")
    if not os.path.exists(gs_path):
        try:
            import urllib.request
            url = "https://raw.githubusercontent.com/RenSolvyn/aegis-framework/main/src/git_sync.py"
            urllib.request.urlretrieve(url, gs_path)
            print("    Downloaded git_sync.py")
        except Exception:
            print("    Skipped git_sync.py (optional)")
    else:
        print(f"    git_sync.py (already exists)")

    # Create program_state.json
    state_path = os.path.join(DRIVE_ROOT, "program_state.json")
    if not os.path.exists(state_path):
        state = {
            "program": {
                "name": PROGRAM_NAME,
                "version": "v1",
                "created": datetime.now(timezone.utc).isoformat(),
                "framework": "aegis-v3.1",
            },
            "last_session": 0,
            "last_session_status": None,
            "last_work_unit": None,
            "last_modified": None,
            "budget": {
                "total_hours": BUDGET_HOURS,
                "spent_hours": 0,
                "remaining_hours": BUDGET_HOURS,
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
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)
        print("    Created program_state.json")
    else:
        print("    program_state.json (already exists — keeping your data)")

    # Create error log
    log_path = os.path.join(DRIVE_ROOT, "logs", "error_log.md")
    if not os.path.exists(log_path):
        with open(log_path, "w") as f:
            f.write(f"# Error Log — {PROGRAM_NAME}\n\n"
                    "Entries appended automatically by Aegis.\n")
        print("    Created error log")

    # Run smoke test
    print()
    print("  Running smoke test...")

    sys.path.insert(0, os.path.join(DRIVE_ROOT, "src"))

    # Clear cached modules
    for mod in ["config", "research_runner", "scientific_method", "git_sync"]:
        if mod in sys.modules:
            del sys.modules[mod]

    try:
        from research_runner import run_experiment, save_result, dashboard

        dashboard()

        def smoke_test(output_dir, program_state):
            results = {"test": "smoke", "status": "passed", "setup": "colab"}
            save_result(os.path.join(output_dir, "smoke.json"), dict(results))
            return {"state_updates": {}, "summary": "Colab setup smoke test"}

        status = run_experiment(
            experiment_fn=smoke_test,
            phase="phase_0",
            work_unit="WU-SETUP",
            expected_outputs=["smoke.json"],
            rigor="explore",
        )

        if status == "COMPLETE":
            print()
            print("  ╔══════════════════════════════════════════╗")
            print("  ║  Setup complete — ready to research      ║")
            print("  ╚══════════════════════════════════════════╝")
            print()
            print("  Your Drive structure:")
            print(f"  Google Drive/{PROJECT_FOLDER}/")
            print(f"  ├── src/              (framework engine)")
            print(f"  ├── scripts/          (your experiments go here)")
            print(f"  ├── results/          (outputs, automatic)")
            print(f"  ├── data/             (your datasets)")
            print(f"  ├── logs/             (error log, automatic)")
            print(f"  ├── docs/             (research plan, notes)")
            print(f"  └── program_state.json (tracks everything)")
            print()
            print("  Every future session, use these 3 cells:")
            print()
            print("  Cell 1 (setup — same every time):")
            print("    from google.colab import drive")
            print("    drive.mount('/content/drive')")
            print("    import os, sys")
            print(f"    os.environ['RESEARCH_DRIVE_ROOT'] = '/content/drive/MyDrive/{PROJECT_FOLDER}'")
            print(f"    sys.path.insert(0, '/content/drive/MyDrive/{PROJECT_FOLDER}/src')")
            print("    from research_runner import dashboard")
            print("    dashboard()")
            print()
            print("  Cell 2 (your experiment — change this each time):")
            print("    !python /content/drive/MyDrive/{}/scripts/YOUR_SCRIPT.py".format(PROJECT_FOLDER))
            print()
            print("  Cell 3 (check results — same every time):")
            print("    dashboard()")
            print()
            return True
        else:
            print(f"\n  Smoke test failed ({status}). Check output above.\n")
            return False

    except Exception as e:
        print(f"\n  Setup error: {e}")
        print("  Try re-running this cell. If it persists, check Drive permissions.\n")
        return False


def _write_if_new(path, content):
    """Write file only if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        print(f"    Created {os.path.basename(path)}")
    else:
        print(f"    {os.path.basename(path)} (already exists)")


if __name__ == "__main__":
    setup()
else:
    # When exec'd in a Colab cell
    setup()
