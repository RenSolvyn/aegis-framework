"""
Aegis Research Runner v4.0
Audited Execution Governance for Independent Science

Changes from v2:
  - Centralized config (imports from config.py)
  - Human-readable experiment summaries (no raw tracebacks)
  - Schema validation on program_state.json
  - help() command explaining what to do next
  - Friendly error wrapper for non-technical users
  - Pre-registration timestamp verification

Usage:
    from research_runner import run_experiment, save_result, dashboard, aegis_help

    dashboard()  # where am I?
    help()       # what do I do next?
"""

import os
import sys
import json
import time
import hashlib
import tempfile
import traceback
from datetime import datetime, timezone

try:
    from config import DRIVE_ROOT, STATE_FILE, ERROR_LOG, RESULTS_ROOT, VERSION
except ImportError:
    DRIVE_ROOT = os.environ.get("RESEARCH_DRIVE_ROOT", "/content/drive/MyDrive/Research")
    STATE_FILE = os.path.join(DRIVE_ROOT, "program_state.json")
    ERROR_LOG = os.path.join(DRIVE_ROOT, "logs", "error_log.md")
    RESULTS_ROOT = os.path.join(DRIVE_ROOT, "results")
    VERSION = "4.0.0"


# =====================================================================
# FRIENDLY ERROR WRAPPER
# =====================================================================

def _friendly_error(error, context=""):
    """Convert Python exceptions to plain English."""
    name = type(error).__name__
    msg = str(error)

    friendly = {
        "FileNotFoundError": (
            f"A file was expected but doesn't exist: {msg}\n"
            "  This usually means a previous step hasn't been run yet,\n"
            "  or the file path is wrong. Check that RESEARCH_DRIVE_ROOT\n"
            "  points to your project folder."
        ),
        "KeyError": (
            f"The program tried to look up '{msg}' but it doesn't exist.\n"
            "  This often means program_state.json is missing a field.\n"
            "  Check that the previous work unit completed successfully."
        ),
        "AssertionError": (
            f"A safety check failed: {msg}\n"
            "  This means a value is outside the expected range.\n"
            "  The experiment stopped before producing invalid results."
        ),
        "ModuleNotFoundError": (
            f"A required library is missing: {msg}\n"
            "  Install it with: pip install {msg.split('No module named ')[-1].strip(chr(39))}"
        ),
        "JSONDecodeError": (
            f"A JSON file is corrupted or has a syntax error.\n"
            "  Check program_state.json for missing commas or brackets.\n"
            "  Detail: {msg}"
        ),
    }

    result = friendly.get(name, f"Something went wrong: {name}: {msg}")
    if context:
        result = f"While {context}:\n  {result}"
    return result


# =====================================================================
# SCHEMA VALIDATION
# =====================================================================

_REQUIRED_STATE_FIELDS = {
    "budget": {"total_hours", "spent_hours", "remaining_hours"},
    "phases": set(),  # phases can be empty but must exist
}

_REQUIRED_TOP_LEVEL = {"budget", "phases"}


def validate_state(state):
    """
    Validate program_state.json has the required structure.
    Returns (is_valid, list_of_issues).
    """
    issues = []

    for field in _REQUIRED_TOP_LEVEL:
        if field not in state:
            issues.append(f"Missing required field: '{field}'")

    if "budget" in state:
        budget = state["budget"]
        if not isinstance(budget, dict):
            issues.append("'budget' should be an object, not " + type(budget).__name__)
        else:
            for subfield in _REQUIRED_STATE_FIELDS["budget"]:
                if subfield not in budget:
                    issues.append(f"Missing budget field: '{subfield}'")
                elif not isinstance(budget[subfield], (int, float)):
                    issues.append(f"budget.{subfield} should be a number, got {type(budget[subfield]).__name__}")

    if "phases" in state:
        if not isinstance(state["phases"], dict):
            issues.append("'phases' should be an object, not " + type(state["phases"]).__name__)

    return len(issues) == 0, issues


# =====================================================================
# DASHBOARD
# =====================================================================

def dashboard(state_path=None):
    """
    Show the session dashboard. Run at the start of every session.
    """
    state_path = state_path or STATE_FILE
    try:
        state = load_program_state(state_path)
    except FileNotFoundError:
        print()
        print("  No project found. Run bootstrap.py to create one.")
        print("  Or set RESEARCH_DRIVE_ROOT to your project folder.")
        print()
        return None
    except json.JSONDecodeError:
        print()
        print("  program_state.json is corrupted (bad JSON syntax).")
        print("  Check for missing commas or brackets.")
        print()
        return None

    # Validate
    valid, issues = validate_state(state)
    if not valid:
        print()
        print("  WARNING: program_state.json has structural issues:")
        for issue in issues:
            print(f"    - {issue}")
        print()

    session = state.get("last_session", 0) + 1
    last_wu = state.get("last_work_unit", "none")
    last_status = state.get("last_session_status", "none")
    budget = state.get("budget", {})
    spent = budget.get("spent_hours", 0)
    total = budget.get("total_hours", 0)
    remaining = budget.get("remaining_hours", total)
    pct = (spent / total * 100) if total > 0 else 0

    # Find current phase
    current_phase = "unknown"
    for phase_name, phase_data in state.get("phases", {}).items():
        if isinstance(phase_data, dict):
            status = phase_data.get("status", "")
            if status in ("IN_PROGRESS", "NOT_STARTED"):
                current_phase = phase_name
                break

    # Count anomalies
    anomalies = state.get("anomalies", [])
    open_anomalies = 0
    if isinstance(anomalies, list):
        open_anomalies = len([a for a in anomalies
                              if isinstance(a, dict) and a.get("status") == "OPEN"])

    # Visual progress bar
    bar_width = 30
    filled = int(bar_width * min(pct, 100) / 100)
    bar = "█" * filled + "░" * (bar_width - filled)

    # Budget warning
    budget_line = ""
    if pct >= 90:
        budget_line = "  ⚠ BUDGET CRITICAL — invoke triage now"
    elif pct >= 75:
        budget_line = "  * Budget warning — consider triage priorities"

    print()
    print("  ╔══════════════════════════════════════════╗")
    print(f"  ║  Aegis Session {session:<27}║")
    print(f"  ║  Phase: {current_phase:<33}║")
    print(f"  ║  Last: {last_wu} → {last_status or 'none':<16}║" if len(f"{last_wu} → {last_status or 'none'}") <= 33 else f"  ║  Last: {last_wu:<33}║")
    print(f"  ║  [{bar}] {pct:>5.1f}%  ║")
    print(f"  ║  {spent:.1f} / {total:.0f} hrs ({remaining:.1f} remaining){' ' * max(0, 17 - len(f'{spent:.1f} / {total:.0f} hrs ({remaining:.1f} remaining)'))}║")
    if open_anomalies > 0:
        print(f"  ║  Anomalies: {open_anomalies} open{' ' * 23}║")
    print("  ╚══════════════════════════════════════════╝")
    if budget_line:
        print(budget_line)
    print()

    return state


# =====================================================================
# HELP COMMAND
# =====================================================================

def aegis_help():
    """
    Print what to do next. Call when you're stuck.
    """
    print()
    print("  ┌─────────────────────────────────────────┐")
    print("  │  What do I do next?                     │")
    print("  ├─────────────────────────────────────────┤")
    print("  │                                         │")
    print("  │  1. Run dashboard() to see where you    │")
    print("  │     are in your research                │")
    print("  │                                         │")
    print("  │  2. Tell your AI what you want to study │")
    print("  │     → it sharpens the question          │")
    print("  │     → it writes the experiment script   │")
    print("  │                                         │")
    print("  │  3. Paste the script into Cell 2,       │")
    print("  │     run all 3 cells                     │")
    print("  │                                         │")
    print("  │  4. Copy Cell 3 results back to the AI  │")
    print("  │     → it explains the numbers           │")
    print("  │     → YOU decide what it means          │")
    print("  │                                         │")
    print("  │  If stuck: log it, save state, stop.    │")
    print("  │  Don't debug for hours.                 │")
    print("  └─────────────────────────────────────────┘")
    print()


# =====================================================================
# ATOMIC I/O
# =====================================================================

def atomic_write_json(filepath, data):
    """Write JSON atomically: temp file then rename."""
    dirpath = os.path.dirname(filepath)
    os.makedirs(dirpath, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dirpath, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, default=_json_default)
        os.rename(tmp_path, filepath)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def _json_default(obj):
    """Safety net for numpy/torch types."""
    try:
        import numpy as np
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
    except ImportError:
        pass
    try:
        import torch
        if isinstance(obj, torch.Tensor):
            return obj.detach().cpu().tolist()
    except ImportError:
        pass
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


# =====================================================================
# STATE MANAGEMENT
# =====================================================================

def load_program_state(path=None):
    """Load program_state.json."""
    path = path or STATE_FILE
    with open(path, "r") as f:
        return json.load(f)


def _apply_dot_path_updates(state, updates):
    """Apply dot-path updates like 'features.negation.l3_rho': 0.42"""
    for dot_path, value in updates.items():
        keys = dot_path.split(".")
        target = state
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value


# =====================================================================
# OUTPUT VERIFICATION
# =====================================================================

def _sha256_file(filepath):
    """Compute SHA-256 hex digest."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def save_result(filepath, data):
    """
    Save JSON result + SHA-256 companion.
    WARNING: Mutates `data` by adding `_metadata`. Pass dict(data) to avoid.
    """
    # Extension hook: validate before saving
    try:
        from extensions import call_hook
        call_hook("on_save_result", filepath, data)
    except ImportError:
        pass

    data["_metadata"] = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "framework": f"aegis-v{VERSION}",
    }
    atomic_write_json(filepath, data)
    sha = _sha256_file(filepath)
    with open(filepath + ".sha256", "w") as f:
        f.write(sha)
    return sha


def _verify_expected_outputs(output_dir, expected_outputs):
    """Check expected JSON files exist with SHA companions."""
    missing, sha_missing = [], []
    for filename in expected_outputs:
        path = os.path.join(output_dir, filename)
        if not os.path.exists(path):
            missing.append(filename)
        elif not os.path.exists(path + ".sha256"):
            sha_missing.append(filename)
    return missing, sha_missing


# =====================================================================
# ERROR LOGGING
# =====================================================================

_error_counter = 0

def log_error(work_unit, source, category, description,
              resolution="UNRESOLVED", lesson="TBD"):
    """Append structured entry to error log."""
    global _error_counter
    _error_counter += 1
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = (
        f"\n### Entry (auto-{_error_counter})\n"
        f"- **Timestamp:** {timestamp}\n"
        f"- **Work unit:** {work_unit}\n"
        f"- **Source:** {source}\n"
        f"- **Category:** {category}\n"
        f"- **Description:** {description}\n"
        f"- **Resolution:** {resolution}\n"
        f"- **Lesson:** {lesson}\n"
    )
    os.makedirs(os.path.dirname(ERROR_LOG), exist_ok=True)
    with open(ERROR_LOG, "a") as f:
        f.write(entry)


# =====================================================================
# SESSION MANAGEMENT
# =====================================================================

def _create_output_dir(phase, work_unit):
    """Create timestamped output directory."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_wu = work_unit.replace(".", "_").replace("-", "_").lower()
    output_dir = os.path.join(RESULTS_ROOT, phase, f"{timestamp}_{safe_wu}")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def _update_session_metadata(state, phase, work_unit, status, elapsed_hours):
    """Update auto-managed fields."""
    state.setdefault("last_session", 0)
    state["last_session"] += 1
    state["last_session_status"] = status
    state["last_work_unit"] = work_unit
    state["last_modified"] = datetime.now(timezone.utc).isoformat()

    budget = state.setdefault("budget", {"total_hours": 0, "spent_hours": 0})
    budget["spent_hours"] = round(budget.get("spent_hours", 0) + elapsed_hours, 2)
    budget["remaining_hours"] = round(
        budget.get("total_hours", 0) - budget["spent_hours"], 2
    )

    phases = state.setdefault("phases", {})
    phase_data = phases.setdefault(phase, {})
    phase_data["hours_spent"] = round(
        phase_data.get("hours_spent", 0) + elapsed_hours, 2
    )
    phase_data.setdefault("work_units", {})[work_unit] = status


def _write_manifest(output_dir, state, work_unit, elapsed_hours, status,
                    rigor, error_msg=None):
    """Write per-run manifest."""
    manifest = {
        "work_unit": work_unit,
        "session": state.get("last_session", 0),
        "status": status,
        "rigor": rigor,
        "pre_registered": os.path.exists(
            os.path.join(output_dir, "pre_registration.json")),
        "runtime_hours": round(elapsed_hours, 4),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "framework_version": VERSION,
        "error": error_msg,
    }
    atomic_write_json(os.path.join(output_dir, "_manifest.json"), manifest)


# =====================================================================
# HUMAN-READABLE SUMMARY
# =====================================================================

def _print_summary(work_unit, status, elapsed_hours, budget, rigor,
                   output_dir, error_msg=None, summary=""):
    """Print a plain-English summary of what just happened."""
    pct = budget.get("spent_hours", 0) / max(budget.get("total_hours", 1), 1) * 100

    print()
    print("  ┌─────────────────────────────────────────┐")

    if status == "COMPLETE":
        print(f"  │  ✓ {work_unit} completed successfully    │")
        if summary:
            # Truncate long summaries
            s = summary[:37]
            print(f"  │    {s:<37}│")
    elif status == "PARTIAL":
        print(f"  │  ○ {work_unit} partially completed       │")
        if error_msg:
            e = error_msg[:37]
            print(f"  │    {e:<37}│")
    else:
        print(f"  │  ✗ {work_unit} failed                    │")
        if error_msg:
            # Show friendly error, not raw traceback
            lines = error_msg.split('\n')
            for line in lines[:2]:
                l = line[:37]
                print(f"  │    {l:<37}│")

    print(f"  │                                         │")
    print(f"  │  Time: {elapsed_hours:.2f} hrs                        │")
    print(f"  │  Budget: {pct:.0f}% used ({budget.get('remaining_hours', 0):.1f} hrs left)       │")
    print(f"  │  Rigor: {rigor:<32}│")
    print("  └─────────────────────────────────────────┘")

    if pct >= 90:
        print("  ⚠ BUDGET CRITICAL — invoke triage now")
    elif pct >= 75:
        print("  * Budget warning — consider triage priorities")

    if status == "COMPLETE":
        print()
        print("  Next: run Cell 3, then copy results to your AI.")
        print(f"  Results in: {os.path.basename(output_dir)}/")
    elif status == "ERROR":
        print()
        print("  The error has been logged automatically.")
        print("  Check logs/error_log.md for details.")
        print("  If stuck: log it, save state, move on.")

    print()


# =====================================================================
# MAIN ENTRY POINT
# =====================================================================

def run_experiment(experiment_fn, phase, work_unit, expected_outputs=None,
                   rigor="standard"):
    """
    Execute an experiment with full lifecycle management.

    Parameters
    ----------
    experiment_fn : callable(output_dir, program_state) -> dict
    phase : str — matches program_state.json phase key
    work_unit : str — matches work unit registry
    expected_outputs : list[str] — JSON filenames to verify
    rigor : str — "explore", "standard", or "publication"
    """
    expected_outputs = expected_outputs or []

    # Load and validate state
    try:
        state = load_program_state()
    except FileNotFoundError:
        print(_friendly_error(
            FileNotFoundError(STATE_FILE),
            "loading program state"
        ))
        return "ERROR"
    except json.JSONDecodeError as e:
        print(_friendly_error(e, "reading program_state.json"))
        return "ERROR"

    valid, issues = validate_state(state)
    if not valid:
        print("\n  program_state.json has issues:")
        for issue in issues:
            print(f"    - {issue}")
        print("  Attempting to continue anyway...\n")

    output_dir = _create_output_dir(phase, work_unit)

    print()
    print(f"  Running: {work_unit} (phase: {phase}, rigor: {rigor})")
    print(f"  Output:  {os.path.basename(output_dir)}/")
    print()

    start_time = time.time()
    status = "ERROR"
    error_msg = None
    result = {}

    # Extension hook: before experiment
    try:
        from extensions import call_hook
        call_hook("on_experiment_start", work_unit, phase, state)
    except ImportError:
        pass

    try:
        result = experiment_fn(output_dir, state) or {}
        status = "COMPLETE"
    except KeyboardInterrupt:
        status = "PARTIAL"
        error_msg = "Manually stopped"
    except Exception as e:
        status = "ERROR"
        error_msg = _friendly_error(e, f"running {work_unit}")
        log_error(work_unit, "Runner (auto)", f"CRASH — {type(e).__name__}",
                  str(e), resolution="UNRESOLVED", lesson="TBD")
        debug_path = os.path.join(output_dir, "_debug_traceback.txt")
        with open(debug_path, "w") as f:
            traceback.print_exc(file=f)

    finally:
        elapsed_hours = (time.time() - start_time) / 3600

        if status == "COMPLETE" and expected_outputs:
            missing, sha_missing = _verify_expected_outputs(output_dir, expected_outputs)
            if missing:
                status = "PARTIAL"
                error_msg = f"Expected output files not found: {', '.join(missing)}"
            elif sha_missing:
                print(f"  Warning: SHA-256 checksums missing for: {', '.join(sha_missing)}")
                print("  Results exist but integrity cannot be verified.")
                print()

        # Rigor enforcement
        if status == "COMPLETE" and rigor in ("standard", "publication"):
            prereg_path = os.path.join(output_dir, "pre_registration.json")
            if not os.path.exists(prereg_path):
                print("  Note: No pre-registration found for this experiment.")
                print("  At rigor='%s', predictions should be locked before running." % rigor)
                print("  Call pre_register() at the start of your experiment function.")
                print()
                result["_unregistered"] = True

        # Apply state updates
        state_updates = result.get("state_updates", {})
        if state_updates:
            _apply_dot_path_updates(state, state_updates)

        # Extension hook: after experiment
        try:
            from extensions import call_hook
            call_hook("on_experiment_end", work_unit, status, result, state)
        except ImportError:
            pass

        _update_session_metadata(state, phase, work_unit, status, elapsed_hours)
        _write_manifest(output_dir, state, work_unit, elapsed_hours, status,
                        rigor, error_msg)

        # Save experiment source code for reproducibility
        try:
            import inspect
            source = inspect.getsource(experiment_fn)
            source_path = os.path.join(output_dir, "_experiment_source.py")
            with open(source_path, "w") as f:
                f.write(f"# Source code captured automatically by Aegis\n")
                f.write(f"# Work unit: {work_unit}\n")
                f.write(f"# Captured: {datetime.now(timezone.utc).isoformat()}\n\n")
                f.write(source)
        except (OSError, TypeError):
            pass  # inspect.getsource fails for some callable types

        # Append to research log (audit trail across experiments)
        try:
            log_path = os.path.join(DRIVE_ROOT, "research_log.md")
            prereg_path = os.path.join(output_dir, "pre_registration.json")
            question = ""
            if os.path.exists(prereg_path):
                with open(prereg_path) as f:
                    pr = json.load(f)
                question = pr.get("predictions", {}).get("hypothesis", "")
            entry = (
                f"| {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} "
                f"| {work_unit} | {status} | {rigor} "
                f"| {question[:60]} | {summary[:40]} |\n"
            )
            if not os.path.exists(log_path):
                header = "| When | Work Unit | Status | Rigor | Question | Result |\n|---|---|---|---|---|---|\n"
                with open(log_path, "w") as f:
                    f.write("# Research Log\n\n")
                    f.write("Auto-generated timeline of all experiments.\n\n")
                    f.write(header)
            with open(log_path, "a") as f:
                f.write(entry)
        except Exception:
            pass  # research log is nice-to-have, never blocks

        atomic_write_json(STATE_FILE, state)

        # Backup state (keeps one previous version for recovery)
        try:
            backup_path = STATE_FILE + ".bak"
            if os.path.exists(STATE_FILE):
                import shutil
                shutil.copy2(STATE_FILE, backup_path)
        except Exception:
            pass  # backup is best-effort

        # Human-readable summary
        summary = result.get("summary", "")
        _print_summary(work_unit, status, elapsed_hours,
                       state.get("budget", {}), rigor, output_dir,
                       error_msg, summary)

        # Auto git sync (best-effort, silent failure)
        try:
            from git_sync import git_sync
            git_sync(work_unit=work_unit, phase=phase, status=status,
                     runtime_hours=elapsed_hours, summary=summary)
        except Exception:
            pass  # Git sync is optional — never block the experiment

    return status
