"""
Aegis One-Click Setup — paste this in Colab and everything is ready.

What this does:
  1. Creates your project structure on Google Drive
  2. Downloads all framework files from GitHub
  3. Saves AI prompts to Drive so you can find them anytime
  4. Saves the Colab notebook template to Drive
  5. Runs a smoke test
  6. Prints exactly what to do next (with copy-paste text)
"""

import os
import sys
import json
import shutil
from datetime import datetime, timezone

# =====================================================================
# CONFIGURATION — change these two lines, then run
# =====================================================================

PROGRAM_NAME = "My Research Program"   # Your research topic
BUDGET_HOURS = 100                     # Your compute budget in hours

# =====================================================================

PROJECT = "Research"
DRIVE_ROOT = f"/content/drive/MyDrive/{PROJECT}"
GITHUB_RAW = "https://raw.githubusercontent.com/RenSolvyn/aegis-framework/main"


def setup():
    # Mount Drive
    try:
        from google.colab import drive
        drive.mount('/content/drive')
    except ImportError:
        print("  This script runs in Google Colab.")
        print("  For local setup, use: python3 bootstrap.py")
        return False

    os.environ["RESEARCH_DRIVE_ROOT"] = DRIVE_ROOT

    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║  Aegis — Setting up your research        ║")
    print("  ╚══════════════════════════════════════════╝")
    print()

    # Create directories
    for d in ["src", "scripts", "results", "data", "logs", "docs", "prompts"]:
        os.makedirs(os.path.join(DRIVE_ROOT, d), exist_ok=True)

    # Download all framework files from GitHub
    files = {
        "src/research_runner.py": "src/research_runner.py",
        "src/scientific_method.py": "src/scientific_method.py",
        "src/config.py": "src/config.py",
        "src/extensions.py": "src/extensions.py",
        "src/git_sync.py": "src/git_sync.py",
        "prompts/creator_prompt.md": "prompts/creator_prompt.md",
        "prompts/auditor_prompt.md": "prompts/auditor_prompt.md",
        "prompts/analyst_prompt.md": "prompts/analyst_prompt.md",
        "prompts/companion_prompt.md": "prompts/companion_prompt.md",
        "prompts/handoff_guide.md": "prompts/handoff_guide.md",
        "examples/colab_notebook.py": "colab_notebook.py",
        "docs/CONCEPTS.md": "docs/CONCEPTS.md",
        "docs/FIRST_SESSION.md": "docs/FIRST_SESSION.md",
        "docs/GUIDE.md": "docs/GUIDE.md",
    }

    import urllib.request
    downloaded = 0
    for github_path, local_path in files.items():
        dest = os.path.join(DRIVE_ROOT, local_path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            urllib.request.urlretrieve(f"{GITHUB_RAW}/{github_path}", dest)
            downloaded += 1
        except Exception as e:
            print(f"    Could not download {github_path}: {e}")

    print(f"  Downloaded {downloaded}/{len(files)} files from GitHub")

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
        print("  Created program_state.json")
    else:
        print("  program_state.json exists (keeping your data)")

    # Create error log
    log_path = os.path.join(DRIVE_ROOT, "logs", "error_log.md")
    if not os.path.exists(log_path):
        with open(log_path, "w") as f:
            f.write(f"# Error Log — {PROGRAM_NAME}\n\n")

    # Smoke test
    print("  Running smoke test...")
    sys.path.insert(0, os.path.join(DRIVE_ROOT, "src"))
    for mod in ["config", "research_runner", "scientific_method"]:
        if mod in sys.modules:
            del sys.modules[mod]

    try:
        from research_runner import run_experiment, save_result, dashboard

        dashboard()

        def smoke(output_dir, program_state):
            save_result(os.path.join(output_dir, "smoke.json"),
                        dict(test="smoke", status="passed"))
            return {"state_updates": {}, "summary": "setup complete"}

        status = run_experiment(smoke, "phase_0", "WU-SETUP",
                                expected_outputs=["smoke.json"], rigor="explore")

        if status != "COMPLETE":
            print(f"\n  Smoke test failed ({status}).\n")
            return False

    except Exception as e:
        print(f"\n  Error: {e}\n")
        return False

    # =========================================================
    # SUCCESS — print everything the user needs
    # =========================================================

    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║  Setup complete!                         ║")
    print("  ╚══════════════════════════════════════════╝")
    print()
    print("  Your project is on Google Drive:")
    print(f"  Drive/{PROJECT}/")
    print(f"  ├── src/       (framework)")
    print(f"  ├── scripts/   (your experiments go here)")
    print(f"  ├── results/   (automatic)")
    print(f"  ├── prompts/   (AI instructions)")
    print(f"  ├── docs/      (guides + concepts glossary)")
    print(f"  └── program_state.json")
    print()
    print()
    print("  ┌─────────────────────────────────────────┐")
    print("  │  WHAT TO DO NEXT (3 steps)              │")
    print("  ├─────────────────────────────────────────┤")
    print("  │                                         │")
    print("  │  1. Open your AI (Claude, ChatGPT...)   │")
    print("  │     Open the file on your Drive:        │")
    print("  │     Drive/Research/prompts/              │")
    print("  │       creator_prompt.md                  │")
    print("  │     Copy its contents and paste it as   │")
    print("  │     the system prompt or first message   │")
    print("  │                                         │")
    print("  │  2. Tell the AI what you want to study: │")
    print("  │     'I want to test whether X affects Y' │")
    print("  │                                         │")
    print("  │  3. The AI writes a script. Upload it   │")
    print("  │     to Drive/Research/scripts/           │")
    print("  │     Then open colab_notebook.py from    │")
    print("  │     Drive/Research/ and run 3 cells.    │")
    print("  │                                         │")
    print("  │  That's it. You're doing research.      │")
    print("  └─────────────────────────────────────────┘")
    print()
    print()
    print("  ── QUICK REFERENCE ──")
    print()
    print("  Your prompts are saved on Drive:")
    print(f"  Drive/{PROJECT}/prompts/creator_prompt.md   → for writing experiments")
    print(f"  Drive/{PROJECT}/prompts/auditor_prompt.md   → for checking scripts")
    print(f"  Drive/{PROJECT}/prompts/analyst_prompt.md   → for reading results")
    print(f"  Drive/{PROJECT}/prompts/companion_prompt.md → all-in-one (casual use)")
    print()
    print("  Your Colab notebook (reuse every session):")
    print(f"  Drive/{PROJECT}/colab_notebook.py")
    print()
    print("  Don't understand a term? Open:")
    print(f"  Drive/{PROJECT}/docs/CONCEPTS.md")
    print()

    return True


setup()
