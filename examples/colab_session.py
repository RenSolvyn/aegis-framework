# ================================================================
# AEGIS — YOUR RESEARCH SESSION
#
# Three cells. You never edit cells 1 or 3.
# Cell 2: just type the script name the AI gave you.
# ================================================================


# ================================================================
# CELL 1: START SESSION (just run it)
# ================================================================

from google.colab import drive
drive.mount('/content/drive')

import os, sys, json, glob
from datetime import datetime

DRIVE_ROOT = "/content/drive/MyDrive/Research"
os.environ["RESEARCH_DRIVE_ROOT"] = DRIVE_ROOT
sys.path.insert(0, os.path.join(DRIVE_ROOT, "src"))

# === DASHBOARD ===
from research_runner import dashboard
state = dashboard()

# === VISUAL PROGRESS ===
if state:
    budget = state.get("budget", {})
    spent = budget.get("spent_hours", 0)
    total = max(budget.get("total_hours", 1), 1)
    pct = min(spent / total * 100, 100)
    bar_width = 40
    filled = int(bar_width * pct / 100)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"  Progress: [{bar}] {pct:.0f}%")
    print()

    # Phase status
    phases = state.get("phases", {})
    for name, data in phases.items():
        if isinstance(data, dict):
            ph_status = data.get("status", "NOT_STARTED")
            wus = data.get("work_units", {})
            done = sum(1 for v in wus.values() if v == "COMPLETE")
            total_wu = len(wus)
            marker = "→" if ph_status == "IN_PROGRESS" else ("✓" if done > 0 else " ")
            print(f"  {marker} {name}: {done} done" + (f" / {total_wu} tracked" if total_wu > 0 else ""))
    print()

# === AVAILABLE SCRIPTS ===
scripts_dir = os.path.join(DRIVE_ROOT, "scripts")
if os.path.exists(scripts_dir):
    all_scripts = []
    for root, dirs, files in os.walk(scripts_dir):
        for f in sorted(files):
            if f.endswith(".py"):
                all_scripts.append(f)
    if all_scripts:
        print(f"  Scripts on Drive ({len(all_scripts)}):")
        for s in all_scripts[-5:]:
            print(f"    {s}")
        if len(all_scripts) > 5:
            print(f"    ... and {len(all_scripts) - 5} more")
    else:
        print("  No scripts on Drive yet.")
        print("  Ask your AI assistant to write one, then upload to Drive/Research/scripts/")
else:
    os.makedirs(scripts_dir, exist_ok=True)
    print("  Created scripts/ folder on Drive.")
    print("  Upload your first script there.")

# === GIT SETUP ===
try:
    from git_sync import git_setup
    git_setup()
except Exception:
    pass

print("\n  Ready. Run Cell 2.\n")


# ================================================================
# CELL 2: RUN YOUR EXPERIMENT
#
# The AI wrote this script. The Auditor approved it.
# You just type the filename below and run this cell.
# ================================================================

SCRIPT = "wu_0_01_baseline.py"  #@param {type:"string"}

# --- Don't edit below this line ---
import os, sys
script_path = None
scripts_dir = os.path.join(os.environ.get("RESEARCH_DRIVE_ROOT", "."), "scripts")

# Search in scripts/ and all subdirectories
for root, dirs, files in os.walk(scripts_dir):
    if SCRIPT in files:
        script_path = os.path.join(root, SCRIPT)
        break

if script_path and os.path.exists(script_path):
    print(f"Running: {SCRIPT}")
    print(f"From: {script_path}")
    print("=" * 50)
    # Execute in the current namespace
    exec(open(script_path).read())
else:
    print(f"Script '{SCRIPT}' not found in {scripts_dir}")
    print()
    print("Options:")
    for root, dirs, files in os.walk(scripts_dir):
        for f in sorted(files):
            if f.endswith(".py"):
                print(f"  {f}")
    print()
    print("Check the filename and make sure it's uploaded to Drive.")


# ================================================================
# CELL 3: SESSION SUMMARY (just run it)
# ================================================================

import json, os
DRIVE_ROOT = os.environ.get("RESEARCH_DRIVE_ROOT", "/content/drive/MyDrive/Research")

# Show updated dashboard
sys.path.insert(0, os.path.join(DRIVE_ROOT, "src"))
from research_runner import dashboard
state = dashboard()

# Find latest results
results_dir = os.path.join(DRIVE_ROOT, "results")
latest_manifest = None
latest_time = 0

if os.path.exists(results_dir):
    for root, dirs, files in os.walk(results_dir):
        if "_manifest.json" in files:
            path = os.path.join(root, "_manifest.json")
            mtime = os.path.getmtime(path)
            if mtime > latest_time:
                latest_time = mtime
                latest_manifest = path

if latest_manifest:
    result_dir = os.path.dirname(latest_manifest)
    with open(latest_manifest) as f:
        manifest = json.load(f)

    print(f"  Latest run: {manifest.get('work_unit', '?')}")
    print(f"  Status: {manifest.get('status', '?')}")
    print(f"  Runtime: {manifest.get('runtime_hours', 0):.2f} hrs")
    print()

    # Print all results
    print("  Results:")
    for fname in sorted(os.listdir(result_dir)):
        fpath = os.path.join(result_dir, fname)
        if fname.endswith(".json") and not fname.startswith("_"):
            print(f"  ── {fname}")
            try:
                with open(fpath) as f:
                    data = json.load(f)
                for k, v in data.items():
                    if not k.startswith("_"):
                        if isinstance(v, float):
                            print(f"     {k}: {v:.6f}")
                        else:
                            print(f"     {k}: {v}")
            except:
                print(f"     (could not parse)")

print()
print("  ────────────────────────────────────")
print("  Copy everything above this line.")
print("  Paste it into your Aegis Companion")
print("  and say: 'analyze results'")
print("  ────────────────────────────────────")
