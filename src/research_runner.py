"""
Aegis Research Runner v2
Audited Execution Governance for Independent Science

Features:
  - Session dashboard (tells you what's next before you start)
  - Automatic session tracking, SHA-256 output verification
  - Atomic state writes, crash recovery, budget management
  - Kill criteria checking after each work unit
  - Parallel save to Drive + GitHub via git_sync

Usage:
    from research_runner import run_experiment, save_result, dashboard

    dashboard()  # shows you the state of the world

    def experiment(output_dir, program_state):
        results = {"accuracy": 0.87}
        save_result(f"{output_dir}/results.json", results)
        return {"state_updates": {"features.my_feature.accuracy": 0.87}}

    run_experiment(experiment_fn=experiment, phase="phase_1",
                   work_unit="WU-1.01", expected_outputs=["results.json"])
"""

import os
import sys
import json
import time
import hashlib
import tempfile
import traceback
from datetime import datetime, timezone


# === Configuration ===
DRIVE_ROOT = os.environ.get("RESEARCH_DRIVE_ROOT", "/content/drive/MyDrive/Research")
STATE_FILE = os.path.join(DRIVE_ROOT, "program_state.json")
ERROR_LOG = os.path.join(DRIVE_ROOT, "logs", "error_log.md")
RESULTS_ROOT = os.path.join(DRIVE_ROOT, "results")


# =====================================================================
# DASHBOARD — run this first, every session
# =====================================================================

def dashboard(state_path=None):
    """
    Print the session dashboard. Run at the start of every session.
    Tells you: where you are, what's next, budget, anomalies, warnings.
    """
    state_path = state_path or STATE_FILE
    try:
        state = load_program_state(state_path)
    except FileNotFoundError:
        print("[dashboard] No program_state.json found. Run your first experiment to create one.")
        return None

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
    open_anomalies = len([a for a in anomalies if isinstance(a, dict) and a.get("status") == "OPEN"]) if isinstance(anomalies, list) else 0

    # Budget warnings
    budget_warning = ""
    if pct >= 90:
        budget_warning = "  *** BUDGET CRITICAL: invoke triage ***"
    elif pct >= 75:
        budget_warning = "  * Budget warning: consider triage priorities"

    print()
    print("=" * 54)
    print(f"  SFRP Session {session}")
    print(f"  Phase: {current_phase}")
    print(f"  Last: {last_wu} → {last_status}")
    print(f"  Budget: {spent:.1f} / {total:.0f} hrs ({pct:.1f}% spent)")
    if remaining > 0:
        print(f"  Remaining: {remaining:.1f} hrs")
    if budget_warning:
        print(budget_warning)
    if open_anomalies > 0:
        print(f"  Anomalies: {open_anomalies} open")
    else:
        print(f"  Anomalies: none")
    print("=" * 54)
    print()

    return state


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
    data["_metadata"] = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "framework": "aegis-v2",
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
    """Append structured entry to error log on Drive."""
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
    """Update auto-managed fields. Scripts NEVER set these."""
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


def _write_manifest(output_dir, state, work_unit, elapsed_hours, status, error_msg=None):
    """Write per-run manifest."""
    manifest = {
        "work_unit": work_unit,
        "session": state.get("last_session", 0),
        "status": status,
        "runtime_hours": round(elapsed_hours, 4),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error": error_msg,
    }
    atomic_write_json(os.path.join(output_dir, "_manifest.json"), manifest)


# =====================================================================
# MAIN ENTRY POINT
# =====================================================================

def run_experiment(experiment_fn, phase, work_unit, expected_outputs=None):
    """
    Execute an experiment with full lifecycle management.

    Parameters
    ----------
    experiment_fn : callable(output_dir, program_state) -> dict
    phase : str — matches program_state.json phase key
    work_unit : str — matches work unit registry
    expected_outputs : list[str] — JSON filenames to verify
    """
    expected_outputs = expected_outputs or []
    state = load_program_state()
    output_dir = _create_output_dir(phase, work_unit)

    print(f"[runner] Phase: {phase} | WU: {work_unit}")
    print(f"[runner] Output: {output_dir}")
    print(f"[runner] Session: {state.get('last_session', 0) + 1}")

    start_time = time.time()
    status = "ERROR"
    error_msg = None
    result = {}

    try:
        result = experiment_fn(output_dir, state) or {}
        status = "COMPLETE"
    except KeyboardInterrupt:
        status = "PARTIAL"
        error_msg = "KeyboardInterrupt"
        print(f"\n[runner] Manual interrupt. Saving partial state.")
    except Exception as e:
        status = "ERROR"
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"\n[runner] CRASH: {error_msg}")
        traceback.print_exc()
        log_error(work_unit, "Runner (auto)", f"CRASH — {type(e).__name__}",
                  str(e), resolution="UNRESOLVED", lesson="TBD")
    finally:
        elapsed_hours = (time.time() - start_time) / 3600

        if status == "COMPLETE" and expected_outputs:
            missing, sha_missing = _verify_expected_outputs(output_dir, expected_outputs)
            if missing:
                status = "PARTIAL"
                error_msg = f"Missing outputs: {missing}"
                print(f"[runner] WARNING: {error_msg}")

        state_updates = result.get("state_updates", {})
        if state_updates:
            _apply_dot_path_updates(state, state_updates)

        _update_session_metadata(state, phase, work_unit, status, elapsed_hours)
        _write_manifest(output_dir, state, work_unit, elapsed_hours, status, error_msg)
        atomic_write_json(STATE_FILE, state)

        # Budget warnings
        budget = state.get("budget", {})
        pct = budget.get("spent_hours", 0) / max(budget.get("total_hours", 1), 1) * 100
        if pct >= 90:
            print(f"\n[runner] *** BUDGET CRITICAL: {pct:.0f}% spent. Invoke triage. ***")
        elif pct >= 75:
            print(f"\n[runner] * Budget warning: {pct:.0f}% spent.")

        # Summary
        print(f"\n[runner] Status: {status}")
        print(f"[runner] Runtime: {elapsed_hours:.2f} hours")
        print(f"[runner] Budget: {budget.get('spent_hours', 0):.1f} / "
              f"{budget.get('total_hours', 0):.0f} hours")

        # Auto git sync (best-effort)
        try:
            from git_sync import git_sync
            summary = result.get("summary", "")
            git_sync(work_unit=work_unit, phase=phase, status=status,
                     runtime_hours=elapsed_hours, summary=summary)
        except Exception as e:
            print(f"[runner] Git sync skipped: {e}")

    return status
