#!/usr/bin/env python3
"""
Aegis Test Suite
Run: python3 tests/test_aegis.py

Tests every component without needing Colab or Drive.
If all tests pass, the framework is ready to use.
"""

import os
import sys
import json
import shutil
import tempfile

# Setup
TEST_DIR = tempfile.mkdtemp(prefix="aegis_test_")
os.environ["RESEARCH_DRIVE_ROOT"] = TEST_DIR
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

passed = 0
failed = 0
errors = []


def test(name):
    """Decorator for test functions."""
    def decorator(fn):
        global passed, failed
        try:
            fn()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            failed += 1
            errors.append((name, str(e)))
    return decorator


# =====================================================================
# Setup: create minimal program_state.json
# =====================================================================

state = {
    "program": {"name": "Test", "version": "v1"},
    "last_session": 0,
    "last_session_status": None,
    "last_work_unit": None,
    "last_modified": None,
    "budget": {"total_hours": 100, "spent_hours": 0, "remaining_hours": 100},
    "calibration": {},
    "features": {},
    "anomalies": [],
    "phases": {"phase_0": {"status": "NOT_STARTED", "hours_spent": 0, "work_units": {}}},
}
os.makedirs(os.path.join(TEST_DIR, "logs"), exist_ok=True)
with open(os.path.join(TEST_DIR, "program_state.json"), "w") as f:
    json.dump(state, f, indent=2)


print()
print("=" * 50)
print("  Aegis Test Suite")
print("=" * 50)
print()


# =====================================================================
# Tests
# =====================================================================

@test("Import research_runner")
def _():
    from research_runner import run_experiment, save_result, dashboard, aegis_help, load_program_state

@test("Import scientific_method")
def _():
    from scientific_method import pre_register, power_check, devils_advocate, literature_check, replication_package, publication_check

@test("Import config")
def _():
    from config import DRIVE_ROOT, VERSION

@test("Load program state")
def _():
    from research_runner import load_program_state
    s = load_program_state()
    assert s["program"]["name"] == "Test"
    assert s["budget"]["total_hours"] == 100

@test("Validate state (valid)")
def _():
    from research_runner import validate_state
    valid, issues = validate_state(state)
    assert valid, f"Should be valid, got issues: {issues}"

@test("Validate state (missing budget)")
def _():
    from research_runner import validate_state
    bad = {"phases": {}}
    valid, issues = validate_state(bad)
    assert not valid
    assert any("budget" in i for i in issues)

@test("Atomic write JSON")
def _():
    from research_runner import atomic_write_json
    path = os.path.join(TEST_DIR, "test_atomic.json")
    atomic_write_json(path, {"hello": "world"})
    with open(path) as f:
        data = json.load(f)
    assert data["hello"] == "world"
    os.remove(path)

@test("Save result + SHA-256")
def _():
    from research_runner import save_result
    path = os.path.join(TEST_DIR, "test_result.json")
    save_result(path, {"accuracy": 0.87})
    assert os.path.exists(path)
    assert os.path.exists(path + ".sha256")
    with open(path) as f:
        data = json.load(f)
    assert data["accuracy"] == 0.87
    assert "_metadata" in data
    os.remove(path)
    os.remove(path + ".sha256")

@test("Dot-path state updates")
def _():
    from research_runner import _apply_dot_path_updates
    s = {"features": {}}
    _apply_dot_path_updates(s, {"features.negation.accuracy": 0.95})
    assert s["features"]["negation"]["accuracy"] == 0.95

@test("Dashboard runs without error")
def _():
    from research_runner import dashboard
    s = dashboard()
    assert s is not None
    assert s["budget"]["total_hours"] == 100

@test("Help runs without error")
def _():
    from research_runner import aegis_help
    aegis_help()  # just verify no crash

@test("Run experiment (complete)")
def _():
    from research_runner import run_experiment, save_result
    def exp(output_dir, program_state):
        save_result(os.path.join(output_dir, "r.json"), {"val": 1})
        return {"state_updates": {"calibration.test": 0.5}, "summary": "test"}
    status = run_experiment(exp, "phase_0", "WU-TEST-1",
                            expected_outputs=["r.json"], rigor="explore")
    assert status == "COMPLETE"
    s = json.load(open(os.path.join(TEST_DIR, "program_state.json")))
    assert s["last_session"] >= 1
    assert s["calibration"]["test"] == 0.5

@test("Run experiment (crash recovery)")
def _():
    from research_runner import run_experiment
    def bad_exp(output_dir, program_state):
        raise ValueError("intentional test error")
    status = run_experiment(bad_exp, "phase_0", "WU-TEST-CRASH",
                            rigor="explore")
    assert status == "ERROR"
    assert os.path.exists(os.path.join(TEST_DIR, "logs", "error_log.md"))

@test("Run experiment (missing outputs)")
def _():
    from research_runner import run_experiment
    def no_output(output_dir, program_state):
        return {}  # doesn't create the expected file
    status = run_experiment(no_output, "phase_0", "WU-TEST-MISSING",
                            expected_outputs=["missing.json"], rigor="explore")
    assert status == "PARTIAL"

@test("Pre-registration")
def _():
    from scientific_method import pre_register, verify_pre_registration
    test_dir = os.path.join(TEST_DIR, "test_prereg")
    pre_register(test_dir, {
        "hypothesis": "test",
        "prediction": "x > 0",
        "null_prediction": "x <= 0",
        "what_would_change_my_mind": "x < -1"
    })
    assert os.path.exists(os.path.join(test_dir, "pre_registration.json"))
    assert verify_pre_registration(test_dir)

@test("Pre-registration tamper detection")
def _():
    from scientific_method import verify_pre_registration
    test_dir = os.path.join(TEST_DIR, "test_prereg")
    # Tamper with the file
    path = os.path.join(test_dir, "pre_registration.json")
    with open(path) as f:
        data = json.load(f)
    data["predictions"]["hypothesis"] = "TAMPERED"
    with open(path, "w") as f:
        json.dump(data, f)
    assert not verify_pre_registration(test_dir)

@test("Power check")
def _():
    from scientific_method import power_check
    result = power_check(effect_size=0.5, alpha=0.05, power=0.80)
    assert result["n_per_group"] > 0
    assert result["total_n"] > result["n_per_group"]

@test("Devil's advocate template")
def _():
    from scientific_method import devils_advocate
    test_dir = os.path.join(TEST_DIR, "test_advocate")
    path = devils_advocate(test_dir, {"result": "test", "effect_size": 0.5,
                                       "p_value": 0.01, "sample_size": 100})
    assert os.path.exists(path)

@test("Publication check")
def _():
    from scientific_method import publication_check
    result = publication_check(TEST_DIR, verbose=False)
    assert "passed" in result
    assert "total" in result
    assert result["total"] == 8

@test("Friendly error messages")
def _():
    from research_runner import _friendly_error
    msg = _friendly_error(FileNotFoundError("test.json"), "loading data")
    assert "doesn't exist" in msg
    msg = _friendly_error(KeyError("missing_key"))
    assert "doesn't exist" in msg


# =====================================================================
# Summary
# =====================================================================

print()
print("=" * 50)
total = passed + failed
print(f"  Results: {passed}/{total} passed")
if failed > 0:
    print(f"  FAILED: {failed}")
    for name, err in errors:
        print(f"    - {name}: {err}")
else:
    print(f"  All tests passed.")
print("=" * 50)
print()

# Cleanup
shutil.rmtree(TEST_DIR)

sys.exit(0 if failed == 0 else 1)
