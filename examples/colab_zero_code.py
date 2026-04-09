# ================================================================
# AEGIS ZERO-CODE COLAB SESSION
#
# You NEVER edit this notebook. You just run the cells.
# Your experiment script lives on Google Drive — the AI wrote it,
# the Auditor checked it, you just run it here.
# ================================================================


# ================================================================
# CELL 1: SETUP (run this, don't change it)
# ================================================================

from google.colab import drive
drive.mount('/content/drive')

import os, sys, glob

# Configure paths
DRIVE_ROOT = "/content/drive/MyDrive/Research"
os.environ["RESEARCH_DRIVE_ROOT"] = DRIVE_ROOT
sys.path.insert(0, os.path.join(DRIVE_ROOT, "src"))

# Show dashboard
from research_runner import dashboard
state = dashboard()

# Find the latest script to run
scripts = sorted(glob.glob(os.path.join(DRIVE_ROOT, "scripts", "*.py")))
if scripts:
    print(f"Scripts on Drive ({len(scripts)}):")
    for s in scripts[-5:]:  # show last 5
        print(f"  {os.path.basename(s)}")
    print(f"\nLatest: {os.path.basename(scripts[-1])}")
else:
    print("No scripts found in Drive/Research/scripts/")
    print("Upload your script there first.")

# Setup git (if configured)
try:
    from git_sync import git_setup
    git_setup()
except Exception:
    pass


# ================================================================
# CELL 2: RUN EXPERIMENT
#
# Change ONLY the filename below to match your script.
# The AI created it. The Auditor approved it. You just run it.
# ================================================================

SCRIPT = "wu_0_01_baseline.py"  # ← change this to your script name

script_path = os.path.join(DRIVE_ROOT, "scripts", SCRIPT)
if os.path.exists(script_path):
    print(f"Running: {SCRIPT}")
    print("=" * 40)
    exec(open(script_path).read())
else:
    print(f"Script not found: {script_path}")
    print(f"Make sure '{SCRIPT}' is in your Drive/Research/scripts/ folder")


# ================================================================
# CELL 3: VERIFY (run this, don't change it)
# ================================================================

# Show updated dashboard
dashboard()

# Show latest results
import json
results_dir = os.path.join(DRIVE_ROOT, "results")
if os.path.exists(results_dir):
    all_results = []
    for root, dirs, files in os.walk(results_dir):
        for f in files:
            if f == "_manifest.json":
                path = os.path.join(root, f)
                all_results.append((os.path.getmtime(path), path))

    if all_results:
        latest = max(all_results, key=lambda x: x[0])
        with open(latest[1]) as f:
            manifest = json.load(f)
        print(f"Latest run: {manifest.get('work_unit', '?')}")
        print(f"Status: {manifest.get('status', '?')}")
        print(f"Runtime: {manifest.get('runtime_hours', 0):.2f} hrs")

        # Show result files in same directory
        result_dir = os.path.dirname(latest[1])
        print(f"\nOutput files:")
        for f in sorted(os.listdir(result_dir)):
            if not f.startswith("_") and not f.endswith(".sha256"):
                print(f"  {f}")
                # Print first few lines of JSON results
                fpath = os.path.join(result_dir, f)
                if f.endswith(".json"):
                    try:
                        with open(fpath) as jf:
                            data = json.load(jf)
                        for k, v in data.items():
                            if not k.startswith("_"):
                                print(f"    {k}: {v}")
                    except:
                        pass

print("\nCopy the output above and bring it to your Analyst conversation.")
