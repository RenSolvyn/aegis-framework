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
        "prompts/aegis_prompt.md": "prompts/aegis_prompt.md",
        "prompts/auditor_prompt.md": "prompts/auditor_prompt.md",
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
    # CREATE COLAB NOTEBOOK on Drive (so user can just open it)
    # =========================================================

    notebook = {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {"colab": {"name": "Aegis Research Session"}, "kernelspec": {"name": "python3", "display_name": "Python 3"}},
        "cells": [
            {"cell_type": "code", "metadata": {}, "source": [
                "# CELL 1: START SESSION (just run this)\n",
                "from google.colab import drive\n",
                "drive.mount('/content/drive')\n",
                "import os, sys, glob\n",
                f"DRIVE_ROOT = '/content/drive/MyDrive/{PROJECT}'\n",
                "os.environ['RESEARCH_DRIVE_ROOT'] = DRIVE_ROOT\n",
                "sys.path.insert(0, os.path.join(DRIVE_ROOT, 'src'))\n",
                "for mod in ['config','research_runner','scientific_method']:\n",
                "    if mod in sys.modules: del sys.modules[mod]\n",
                "from research_runner import dashboard\n",
                "dashboard()\n",
                "scripts = sorted(glob.glob(os.path.join(DRIVE_ROOT,'scripts','*.py')))\n",
                "if scripts: print(f'  Latest script: {os.path.basename(scripts[-1])}')\n",
                "else: print('  No scripts yet. Upload one to Drive/Research/scripts/')\n",
            ], "outputs": [], "execution_count": None},
            {"cell_type": "code", "metadata": {}, "source": [
                "# CELL 2: RUN EXPERIMENT\\n",
                "# Option A: Paste your script below and run this cell\\n",
                "# Option B: Upload .py to Drive/Research/scripts/ and run this cell\\n",
                "#           (it auto-detects the latest script)\\n",
                "import os, sys, glob\\n",
                "DRIVE_ROOT = os.environ.get('RESEARCH_DRIVE_ROOT','')\\n",
                "scripts = sorted(glob.glob(os.path.join(DRIVE_ROOT, 'scripts', '*.py')))\\n",
                "if scripts:\\n",
                "    print(f'Running: {os.path.basename(scripts[-1])}')\\n",
                "    print('=' * 50)\\n",
                "    exec(open(scripts[-1]).read())\\n",
                "else:\\n",
                "    print('Paste your experiment script below this line and re-run,')\\n",
                "    print('or upload a .py file to Drive/Research/scripts/')\\n",
            ], "outputs": [], "execution_count": None},
            {"cell_type": "code", "metadata": {}, "source": [
                "# CELL 3: RESULTS (copy output to your AI)\n",
                "import json, os, sys\n",
                "DRIVE_ROOT = os.environ.get('RESEARCH_DRIVE_ROOT','')\n",
                "sys.path.insert(0, os.path.join(DRIVE_ROOT, 'src'))\n",
                "for mod in ['config','research_runner']: \n",
                "    if mod in sys.modules: del sys.modules[mod]\n",
                "from research_runner import dashboard\n",
                "dashboard()\n",
                "results_dir = os.path.join(DRIVE_ROOT, 'results')\n",
                "latest_manifest = None; latest_time = 0\n",
                "if os.path.exists(results_dir):\n",
                "    for root, dirs, files in os.walk(results_dir):\n",
                "        if '_manifest.json' in files:\n",
                "            path = os.path.join(root, '_manifest.json')\n",
                "            mtime = os.path.getmtime(path)\n",
                "            if mtime > latest_time: latest_time = mtime; latest_manifest = path\n",
                "if latest_manifest:\n",
                "    result_dir = os.path.dirname(latest_manifest)\n",
                "    with open(latest_manifest) as f: manifest = json.load(f)\n",
                "    print('-' * 50)\n",
                "    print('  COPY EVERYTHING BELOW TO YOUR AI')\n",
                "    print('-' * 50)\n",
                "    print(f'Work unit: {manifest.get(\"work_unit\",\"?\")}')\n",
                "    print(f'Status: {manifest.get(\"status\",\"?\")}')\n",
                "    print(f'Rigor: {manifest.get(\"rigor\",\"?\")}')\n",
                "    print()\n",
                "    prereg = os.path.join(result_dir, 'pre_registration.json')\n",
                "    if os.path.exists(prereg):\n",
                "        with open(prereg) as f: pr = json.load(f)\n",
                "        preds = pr.get('predictions', {})\n",
                "        print('PREDICTIONS (locked before experiment):')\n",
                "        for k, v in preds.items():\n",
                "            print(f'  {k}: {v}')\n",
                "        aplan = pr.get('analysis_plan', {})\n",
                "        if aplan:\n",
                "            print('ANALYSIS PLAN (locked before experiment):')\n",
                "            for k, v in aplan.items():\n",
                "                print(f'  {k}: {v}')\n",
                "        print()\n",
                "    print('RESULTS (observed):')\n",
                "    for fname in sorted(os.listdir(result_dir)):\n",
                "        if fname.endswith('.json') and not fname.startswith('_') and fname != 'pre_registration.json':\n",
                "            print(f'  -- {fname} --')\n",
                "            try:\n",
                "                with open(os.path.join(result_dir, fname)) as f: data = json.load(f)\n",
                "                for k, v in data.items():\n",
                "                    if not k.startswith('_'): print(f'    {k}: {v}')\n",
                "            except: print('    (could not parse)')\n",
                "    print()\n",
                "    from scientific_method import blind_interpret\n",
                "    interp = blind_interpret(result_dir)\n",
                "    if interp: print(interp); print()\n",
                "    print()\n",
                "    print('-' * 50)\n",
                "    print('  STOP COPYING HERE')\n",
                "    print('-' * 50)\n",
                "    print()\n",
                "    print('  Paste to your AI and say: analyze these results')\n",
            ], "outputs": [], "execution_count": None},
        ]
    }

    nb_path = os.path.join(DRIVE_ROOT, "Aegis_Research_Session.ipynb")
    with open(nb_path, "w") as f:
        json.dump(notebook, f, indent=2)
    print("  Created Aegis_Research_Session.ipynb on Drive")

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
    print("  │  WHAT TO DO NEXT (one time only)        │")
    print("  ├─────────────────────────────────────────┤")
    print("  │                                         │")
    print("  │  1. Open Drive/Research/prompts/         │")
    print("  │     aegis_prompt.md                      │")
    print("  │                                         │")
    print("  │  2. Copy ALL the text inside             │")
    print("  │                                         │")
    print("  │  3. Open any AI (Claude, ChatGPT, etc)   │")
    print("  │     Paste it as your first message       │")
    print("  │                                         │")
    print("  │  4. Tell the AI what you're curious about│")
    print("  │     It handles everything from there.    │")
    print("  │                                         │")
    print("  │  That's it. You're doing research.      │")
    print("  └─────────────────────────────────────────┘")
    print()
    print()
    print("  ── QUICK REFERENCE ──")
    print()
    print("  Your AI prompt:")
    print(f"  Drive/{PROJECT}/prompts/aegis_prompt.md")
    print()
    print("  Your Colab notebook (reuse every session):")
    print(f"  Drive/{PROJECT}/Aegis_Research_Session.ipynb")
    print()
    print("  Don't understand a term? Open:")
    print(f"  Drive/{PROJECT}/docs/CONCEPTS.md")
    print()

    return True


setup()
