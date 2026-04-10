# ================================================================
# AEGIS — YOUR RESEARCH SESSION
#
# This is the ONLY Colab file you need. It handles everything:
# - First time? Creates your project on Drive automatically
# - Returning? Shows your dashboard and runs your latest script
#
# You NEVER edit this notebook. Just run the cells.
# ================================================================


# ================================================================
# CELL 1: START (run this every session — it handles everything)
# ================================================================

# Mount Drive
from google.colab import drive
drive.mount('/content/drive')

import os, sys, json, glob

# Configuration
PROJECT = "Research"  # Your project folder name on Drive
DRIVE_ROOT = f"/content/drive/MyDrive/{PROJECT}"
os.environ["RESEARCH_DRIVE_ROOT"] = DRIVE_ROOT

# First-time setup: create project if it doesn't exist
if not os.path.exists(os.path.join(DRIVE_ROOT, "program_state.json")):
    print("\n  First time? Setting up your project...\n")
    try:
        import urllib.request
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/RenSolvyn/aegis-framework/main/examples/colab_setup.py",
            "/content/setup.py")
        exec(open("/content/setup.py").read())
    except Exception as e:
        print(f"  Setup failed: {e}")
        print("  Check your internet connection and try again.")
else:
    # Returning session: show dashboard
    sys.path.insert(0, os.path.join(DRIVE_ROOT, "src"))

    # Update framework from GitHub (silent, best-effort)
    for module in ["research_runner.py", "scientific_method.py", "config.py"]:
        try:
            import urllib.request
            urllib.request.urlretrieve(
                f"https://raw.githubusercontent.com/RenSolvyn/aegis-framework/main/src/{module}",
                os.path.join(DRIVE_ROOT, "src", module))
        except:
            pass

    # Clear cached modules
    for mod in ["config", "research_runner", "scientific_method"]:
        if mod in sys.modules:
            del sys.modules[mod]

    from research_runner import dashboard, aegis_help
    dashboard()

    # Show available scripts
    scripts_dir = os.path.join(DRIVE_ROOT, "scripts")
    if os.path.exists(scripts_dir):
        scripts = sorted([f for f in os.listdir(scripts_dir) if f.endswith(".py")])
        if scripts:
            print(f"  Scripts ({len(scripts)}):")
            for s in scripts[-5:]:
                print(f"    {s}")
            print(f"\n  Latest: {scripts[-1]}")
            print(f"  Cell 2 will run this automatically.\n")
        else:
            print("  No scripts yet. Ask your AI to write one,")
            print("  then upload it to Drive/Research/scripts/\n")
    else:
        os.makedirs(scripts_dir, exist_ok=True)
        print("  Created scripts/ folder.\n")

    # Git setup (silent)
    try:
        from git_sync import git_setup
        git_setup()
    except:
        pass


# ================================================================
# CELL 2: RUN EXPERIMENT (runs the latest script automatically)
# ================================================================

import os, sys, glob

DRIVE_ROOT = os.environ.get("RESEARCH_DRIVE_ROOT", "/content/drive/MyDrive/Research")
scripts_dir = os.path.join(DRIVE_ROOT, "scripts")

# Find the newest script
scripts = sorted(glob.glob(os.path.join(scripts_dir, "*.py")))

if not scripts:
    print("  No scripts found in Drive/Research/scripts/")
    print()
    print("  To create one:")
    print("  1. Open your Creator AI conversation")
    print("  2. Describe what you want to study")
    print("  3. Get the script approved by the Auditor")
    print("  4. Upload it to Drive/Research/scripts/")
    print("  5. Re-run this cell")
else:
    latest = scripts[-1]
    name = os.path.basename(latest)
    print(f"  Running: {name}")
    print("=" * 50)
    exec(open(latest).read())


# ================================================================
# CELL 3: RESULTS (copy this output to your Analyst AI)
# ================================================================

import json, os, sys

DRIVE_ROOT = os.environ.get("RESEARCH_DRIVE_ROOT", "/content/drive/MyDrive/Research")
sys.path.insert(0, os.path.join(DRIVE_ROOT, "src"))
for mod in ["config", "research_runner"]:
    if mod in sys.modules:
        del sys.modules[mod]

from research_runner import dashboard
dashboard()

# Find and display latest results
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

    print("─" * 50)
    print("  COPY EVERYTHING BELOW TO YOUR AI")
    print("─" * 50)
    print()
    print(f"Work unit: {manifest.get('work_unit', '?')}")
    print(f"Status: {manifest.get('status', '?')}")
    print(f"Runtime: {manifest.get('runtime_hours', 0):.2f} hrs")
    print(f"Rigor: {manifest.get('rigor', '?')}")
    print(f"Pre-registered: {manifest.get('pre_registered', False)}")
    print()

    # Print all result files
    for fname in sorted(os.listdir(result_dir)):
        fpath = os.path.join(result_dir, fname)
        if fname.endswith(".json") and not fname.startswith("_"):
            print(f"── {fname} ──")
            try:
                with open(fpath) as f:
                    data = json.load(f)
                for k, v in data.items():
                    if k.startswith("_"):
                        continue
                    if isinstance(v, float):
                        print(f"  {k}: {v:.6f}")
                    elif isinstance(v, dict):
                        print(f"  {k}:")
                        for k2, v2 in v.items():
                            print(f"    {k2}: {v2}")
                    else:
                        print(f"  {k}: {v}")
            except:
                print("  (could not parse)")
            print()

    print("─" * 50)
    print("  STOP COPYING HERE")
    print("─" * 50)
    print()
    print("  Paste everything between the lines to your")
    print("  Analyst AI and say: 'analyze these results'")
else:
    print("  No results yet. Run Cell 2 first.")
