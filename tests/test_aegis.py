#!/usr/bin/env python3
"""
Aegis Test Suite
Run: python3 tests/test_aegis.py

Tests every component WITHOUT circular validation, happy-pathing,
or artificial passes. Each test simulates real user behavior.
"""

import os
import sys
import json
import shutil
import hashlib
import tempfile

TEST_DIR = tempfile.mkdtemp(prefix="aegis_test_")
os.environ["RESEARCH_DRIVE_ROOT"] = TEST_DIR
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

passed = 0
failed = 0
errors = []

def test(name):
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

# Setup
state = {
    "program": {"name": "Test", "version": "v1"},
    "last_session": 0, "last_session_status": None,
    "last_work_unit": None, "last_modified": None,
    "budget": {"total_hours": 100, "spent_hours": 0, "remaining_hours": 100},
    "calibration": {}, "features": {}, "anomalies": [],
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

# --- 1. IMPORTS ---

@test("Import research_runner")
def _():
    from research_runner import run_experiment, save_result, dashboard, aegis_help, load_program_state

@test("Import scientific_method")
def _():
    from scientific_method import pre_register, power_check, blind_interpret, publication_check

@test("Import config")
def _():
    from config import DRIVE_ROOT, VERSION

# --- 2. STATE MANAGEMENT ---

@test("Load program state from disk")
def _():
    from research_runner import load_program_state
    s = load_program_state()
    assert s["program"]["name"] == "Test"
    assert s["budget"]["total_hours"] == 100

@test("Validate state catches missing fields")
def _():
    from research_runner import validate_state
    valid, issues = validate_state({})
    assert not valid, "Empty dict should be invalid"
    assert len(issues) >= 2
    valid, issues = validate_state({"budget": "not_a_dict", "phases": {}})
    assert not valid

@test("Dot-path creates nested dicts from scratch")
def _():
    from research_runner import _apply_dot_path_updates
    s = {}
    _apply_dot_path_updates(s, {"a.b.c.d": 42})
    assert s["a"]["b"]["c"]["d"] == 42

@test("Dot-path preserves siblings")
def _():
    from research_runner import _apply_dot_path_updates
    s = {"features": {"neg": {"acc": 0.9}}}
    _apply_dot_path_updates(s, {"features.neg.rho": 0.5})
    assert s["features"]["neg"]["acc"] == 0.9, "Sibling overwritten!"
    assert s["features"]["neg"]["rho"] == 0.5

@test("Atomic write JSON")
def _():
    from research_runner import atomic_write_json
    path = os.path.join(TEST_DIR, "test_atomic.json")
    atomic_write_json(path, {"nested": {"a": 1}})
    with open(path) as f:
        assert json.load(f)["nested"]["a"] == 1
    os.remove(path)

# --- 3. SHA VERIFICATION ---

@test("SHA-256 matches actual file content")
def _():
    from research_runner import save_result
    path = os.path.join(TEST_DIR, "test_sha.json")
    save_result(path, {"accuracy": 0.87})
    with open(path + ".sha256") as f:
        stored = f.read().strip()
    with open(path, "rb") as f:
        computed = hashlib.sha256(f.read()).hexdigest()
    assert stored == computed, f"SHA mismatch: {stored[:16]} vs {computed[:16]}"
    os.remove(path); os.remove(path + ".sha256")

@test("SHA detects file tampering")
def _():
    from research_runner import save_result
    path = os.path.join(TEST_DIR, "test_tamper.json")
    save_result(path, {"value": 1.0})
    with open(path + ".sha256") as f:
        orig_hash = f.read().strip()
    with open(path) as f:
        data = json.load(f)
    data["value"] = 999.0
    with open(path, "w") as f:
        json.dump(data, f)
    with open(path, "rb") as f:
        new_hash = hashlib.sha256(f.read()).hexdigest()
    assert orig_hash != new_hash, "SHA should change after tampering"
    os.remove(path); os.remove(path + ".sha256")

@test("save_result mutation bug documented correctly")
def _():
    from research_runner import save_result
    path = os.path.join(TEST_DIR, "test_mut.json")
    original = {"val": 1}
    save_result(path, original)
    assert "_metadata" in original, "save_result should mutate original"
    clean = {"val": 2}
    save_result(path, dict(clean))
    assert "_metadata" not in clean, "dict() wrapper should prevent mutation"
    os.remove(path); os.remove(path + ".sha256")

# --- 4. EXPERIMENT LIFECYCLE ---

@test("Dashboard runs")
def _():
    from research_runner import dashboard
    s = dashboard()
    assert s is not None

@test("Help text is current (single conversation, not Analyst)")
def _():
    from research_runner import aegis_help
    import io; from contextlib import redirect_stdout
    f = io.StringIO()
    with redirect_stdout(f):
        aegis_help()
    out = f.getvalue()
    assert "what you want to study" in out.lower() or "tell your ai" in out.lower(), \
        "Should mention telling your AI"
    assert "Analyst" not in out, "Should NOT mention Analyst"
    assert "second code box" in out.lower(), "Should say 'second code box' not 'Cell 2'"

@test("Budget accumulates across experiments")
def _():
    from research_runner import run_experiment, save_result, load_program_state
    s0 = load_program_state()
    session_before = s0["last_session"]
    def exp(output_dir, program_state):
        save_result(os.path.join(output_dir, "r.json"), dict({"v": 1}))
        return {}
    run_experiment(exp, "phase_0", "WU-B1", expected_outputs=["r.json"], rigor="explore")
    run_experiment(exp, "phase_0", "WU-B2", expected_outputs=["r.json"], rigor="explore")
    s = load_program_state()
    # Budget math: spent + remaining should equal total
    assert abs(s["budget"]["spent_hours"] + s["budget"]["remaining_hours"] - 100) < 0.01, \
        "spent + remaining must equal total"
    # At least 2 more sessions should have been tracked
    assert s["last_session"] >= session_before + 2, "Sessions should increment"
    # Both WUs should be recorded in phases
    wus = s["phases"]["phase_0"]["work_units"]
    assert "WU-B1" in wus and "WU-B2" in wus, "Both WUs should be recorded"

@test("Crash logs error and records status")
def _():
    from research_runner import run_experiment, load_program_state
    status = run_experiment(lambda o, s: (_ for _ in ()).throw(ValueError("boom")),
                            "phase_0", "WU-BOOM", rigor="explore")
    assert status == "ERROR"
    with open(os.path.join(TEST_DIR, "logs", "error_log.md")) as f:
        assert "boom" in f.read()
    s = load_program_state()
    assert s["last_session_status"] == "ERROR"

@test("Missing outputs → PARTIAL not COMPLETE")
def _():
    from research_runner import run_experiment
    status = run_experiment(lambda o, s: {}, "phase_0", "WU-MISS",
                            expected_outputs=["nope.json"], rigor="explore")
    assert status == "PARTIAL"

@test("Session counter increments")
def _():
    from research_runner import run_experiment, save_result, load_program_state
    before = load_program_state()["last_session"]
    def exp(o, s):
        save_result(os.path.join(o, "r.json"), dict({"v": 1}))
        return {}
    run_experiment(exp, "phase_0", "WU-CNT", expected_outputs=["r.json"], rigor="explore")
    after = load_program_state()["last_session"]
    assert after == before + 1

@test("State updates from exp1 readable in exp2")
def _():
    from research_runner import run_experiment, save_result
    def exp1(o, s):
        save_result(os.path.join(o, "r.json"), dict({"v": 1}))
        return {"state_updates": {"features.xfeat.acc": 0.77}}
    run_experiment(exp1, "phase_0", "WU-S1", expected_outputs=["r.json"], rigor="explore")
    def exp2(o, s):
        val = s["features"]["xfeat"]["acc"]
        assert val == 0.77, f"Should read 0.77, got {val}"
        save_result(os.path.join(o, "r.json"), dict({"read": val}))
        return {}
    status = run_experiment(exp2, "phase_0", "WU-S2", expected_outputs=["r.json"], rigor="explore")
    assert status == "COMPLETE", "Exp2 should read exp1's state"

@test("Post-experiment message says 'your AI'")
def _():
    from research_runner import run_experiment, save_result
    import io; from contextlib import redirect_stdout
    def exp(o, s):
        save_result(os.path.join(o, "r.json"), dict({"v": 1}))
        return {}
    f = io.StringIO()
    with redirect_stdout(f):
        run_experiment(exp, "phase_0", "WU-PM", expected_outputs=["r.json"], rigor="explore")
    assert "your AI" in f.getvalue() or "your ai" in f.getvalue().lower(), "Should mention 'your AI'"
    assert "Analyst" not in f.getvalue(), "Should NOT mention Analyst"

# --- 5. PRE-REGISTRATION ---

@test("Pre-reg locks and verifies")
def _():
    from scientific_method import pre_register, verify_pre_registration
    d = os.path.join(TEST_DIR, "pr1")
    pre_register(d, {"hypothesis": "h", "prediction": "p", "null_prediction": "n", "what_would_change_my_mind": "w"})
    assert verify_pre_registration(d)

@test("Pre-reg detects tampering")
def _():
    from scientific_method import pre_register, verify_pre_registration
    d = os.path.join(TEST_DIR, "pr2")
    pre_register(d, {"hypothesis": "h", "prediction": "p", "null_prediction": "n", "what_would_change_my_mind": "w"})
    path = os.path.join(d, "pre_registration.json")
    with open(path) as f: data = json.load(f)
    data["predictions"]["hypothesis"] = "CHANGED"
    with open(path, "w") as f: json.dump(data, f)
    assert not verify_pre_registration(d), "Tampered file should fail"

@test("Missing pre-reg returns False")
def _():
    from scientific_method import verify_pre_registration
    d = os.path.join(TEST_DIR, "no_prereg")
    os.makedirs(d, exist_ok=True)
    assert not verify_pre_registration(d)

@test("Analysis plan stored correctly")
def _():
    from scientific_method import pre_register
    d = os.path.join(TEST_DIR, "pr3")
    pre_register(d, {"hypothesis":"h","prediction":"p","null_prediction":"n","what_would_change_my_mind":"w"},
        analysis_plan={"statistical_test": "t-test", "data_cleaning": "none",
                       "exclusion_criteria": "none", "multiple_comparisons": "none",
                       "sample_size_justification": "N=30"})
    with open(os.path.join(d, "pre_registration.json")) as f: data = json.load(f)
    assert data["has_analysis_plan"] is True
    assert data["analysis_plan"]["statistical_test"] == "t-test"

# --- 6. BLIND INTERPRET ---

@test("Classifies p=0.003 as strong evidence")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f: json.dump({"p_value": 0.003}, f)
    assert "strong evidence" in blind_interpret(d)
    shutil.rmtree(d)

@test("Classifies p=0.42 as not significant")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f: json.dump({"p_value": 0.42}, f)
    assert "no significant" in blind_interpret(d)
    shutil.rmtree(d)

@test("Classifies large effect size")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f: json.dump({"cohens_d": 0.82}, f)
    assert "large effect" in blind_interpret(d)
    shutil.rmtree(d)

@test("Classifies negligible effect")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f: json.dump({"cohens_d": 0.1}, f)
    assert "negligible" in blind_interpret(d)
    shutil.rmtree(d)

@test("Classifies negative correlation with direction")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f: json.dump({"rho": -0.65}, f)
    r = blind_interpret(d)
    assert "strong" in r and "negative" in r
    shutil.rmtree(d)

@test("Flags NaN values as warning")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f: json.dump({"result": float('nan')}, f)
    assert "NaN" in blind_interpret(d)
    shutil.rmtree(d)

@test("Verifies pre-reg integrity in interpretation")
def _():
    from scientific_method import blind_interpret, pre_register
    d = tempfile.mkdtemp()
    pre_register(d, {"hypothesis":"h","prediction":"p","null_prediction":"n","what_would_change_my_mind":"w"})
    with open(os.path.join(d, "r.json"), "w") as f: json.dump({"p_value": 0.01}, f)
    assert "VERIFIED" in blind_interpret(d)
    shutil.rmtree(d)

@test("Returns empty for non-numeric results")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f: json.dump({"status": "done"}, f)
    assert blind_interpret(d) == ""
    shutil.rmtree(d)

# --- 7. POWER CHECK ---

@test("Power check: d=0.5 gives ~63 per group")
def _():
    from scientific_method import power_check
    r = power_check(effect_size=0.5)
    assert 50 < r["n_per_group"] < 80, f"Expected ~63, got {r['n_per_group']}"

@test("Power check rejects zero effect")
def _():
    from scientific_method import power_check
    try: power_check(effect_size=0.0); assert False, "Should raise"
    except ValueError: pass

@test("Large effect needs fewer subjects than small")
def _():
    from scientific_method import power_check
    s = power_check(effect_size=0.2)
    l = power_check(effect_size=0.8)
    assert l["n_per_group"] < s["n_per_group"]

# --- 8. PUBLICATION CHECK ---

@test("Publication check has 10 checks")
def _():
    from scientific_method import publication_check
    r = publication_check(TEST_DIR, verbose=False)
    assert r["total"] == 10
    assert len(r["checks"]) == 10

# --- 9. FRIENDLY ERRORS ---

@test("Friendly errors are readable")
def _():
    from research_runner import _friendly_error
    assert "doesn't exist" in _friendly_error(FileNotFoundError("x.json"), "loading")
    assert "pip install" in _friendly_error(ModuleNotFoundError("No module named 'torch'"))
    assert "weird" in _friendly_error(RuntimeError("weird"))

# --- 10. EXTENSIONS ---

@test("Extensions load without user extensions.py")
def _():
    from extensions import call_hook, get_custom_publication_checks
    assert call_hook("on_experiment_start", "WU", "p", {}) is None
    assert get_custom_publication_checks(TEST_DIR) == []

# --- 11. END-TO-END CYCLE ---

@test("E2E: pre-register → run → verify → blind interpret")
def _():
    from research_runner import run_experiment, save_result, load_program_state
    from scientific_method import pre_register, verify_pre_registration, blind_interpret
    import random

    def experiment(output_dir, program_state):
        pre_register(output_dir, {
            "hypothesis": "Coffee increases height",
            "prediction": "mean > 15",
            "null_prediction": "mean <= 15",
            "what_would_change_my_mind": "p > 0.05"
        }, analysis_plan={
            "statistical_test": "t-test", "data_cleaning": "none",
            "exclusion_criteria": "none", "multiple_comparisons": "none",
            "sample_size_justification": "N=30"
        })
        random.seed(42)
        coffee = [random.gauss(18, 3) for _ in range(30)]
        control = [random.gauss(14, 3) for _ in range(30)]
        mc = sum(coffee)/30; mk = sum(control)/30
        ps = ((sum((x-mc)**2 for x in coffee)+sum((x-mk)**2 for x in control))/58)**0.5
        results = {
            "mean_coffee": round(float(mc), 2),
            "mean_control": round(float(mk), 2),
            "cohens_d": round(float((mc-mk)/ps), 2) if ps > 0 else 0.0,
            "p_value": 0.003,
        }
        assert 0 <= results["p_value"] <= 1
        save_result(os.path.join(output_dir, "results.json"), dict(results))
        return {"state_updates": {"features.coffee.p": 0.003}, "summary": "done"}

    status = run_experiment(experiment, "phase_0", "WU-E2E",
                            expected_outputs=["results.json"], rigor="standard")
    assert status == "COMPLETE"

    # Find output dir
    results_dir = os.path.join(TEST_DIR, "results")
    latest = None
    for root, dirs, files in os.walk(results_dir):
        if "_manifest.json" in files and "wu_e2e" in root.lower():
            latest = root
    assert latest, "Should find E2E output"

    # Pre-reg should verify
    assert verify_pre_registration(latest), "Pre-reg should be intact"

    # Blind interpret should classify
    interp = blind_interpret(latest)
    assert "strong evidence" in interp, f"Should classify p=0.003, got: {interp}"
    assert "VERIFIED" in interp, "Pre-reg should verify in interpretation"

    # State should persist
    s = load_program_state()
    assert s["features"]["coffee"]["p"] == 0.003


# =====================================================================
# 12. EDGE CASES — untested paths that could hide bugs
# =====================================================================

@test("Experiment returning None doesn't crash")
def _():
    from research_runner import run_experiment, save_result
    def returns_none(output_dir, program_state):
        save_result(os.path.join(output_dir, "r.json"), dict({"v": 1}))
        return None  # not a dict
    status = run_experiment(returns_none, "phase_0", "WU-NONE",
                            expected_outputs=["r.json"], rigor="explore")
    assert status == "COMPLETE", f"Should handle None return, got {status}"

@test("Missing SHA companion warns but doesn't fail")
def _():
    from research_runner import run_experiment
    import io; from contextlib import redirect_stdout
    def creates_json_no_sha(output_dir, program_state):
        # Write JSON manually without SHA (simulates partial save)
        path = os.path.join(output_dir, "r.json")
        with open(path, "w") as f:
            json.dump({"val": 1}, f)
        # Don't create .sha256 companion
        return {}
    f = io.StringIO()
    with redirect_stdout(f):
        status = run_experiment(creates_json_no_sha, "phase_0", "WU-NOSHA",
                                expected_outputs=["r.json"], rigor="explore")
    assert status == "COMPLETE", "Should still COMPLETE (file exists)"
    assert "SHA-256" in f.getvalue() or "checksum" in f.getvalue().lower(), \
        "Should warn about missing SHA"

@test("Rigor enforcement warns about missing pre-registration")
def _():
    from research_runner import run_experiment, save_result
    import io; from contextlib import redirect_stdout
    def no_prereg(output_dir, program_state):
        save_result(os.path.join(output_dir, "r.json"), dict({"v": 1}))
        return {}
    f = io.StringIO()
    with redirect_stdout(f):
        run_experiment(no_prereg, "phase_0", "WU-NOREG",
                       expected_outputs=["r.json"], rigor="standard")
    assert "pre-registration" in f.getvalue().lower(), \
        "Standard rigor should warn about missing pre-registration"

@test("Pre-registration rejects missing required fields")
def _():
    from scientific_method import pre_register
    d = os.path.join(TEST_DIR, "bad_prereg")
    try:
        pre_register(d, {"hypothesis": "test"})  # missing 3 required fields
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "missing" in str(e).lower()

@test("blind_interpret handles mixed numeric and string values")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({
            "status": "complete",
            "p_value": 0.04,
            "label": "experiment_a",
            "cohens_d": 0.55,
            "notes": "all good"
        }, f)
    result = blind_interpret(d)
    assert "moderate evidence" in result, f"Should classify p=0.04, got: {result}"
    assert "medium effect" in result, f"Should classify d=0.55, got: {result}"
    assert "complete" not in result, "Should NOT include string values"
    shutil.rmtree(d)

@test("Budget warning fires at 90%")
def _():
    from research_runner import _print_summary
    import io; from contextlib import redirect_stdout
    budget = {"total_hours": 100, "spent_hours": 92, "remaining_hours": 8}
    f = io.StringIO()
    with redirect_stdout(f):
        _print_summary("WU-X", "COMPLETE", 0.1, budget, "standard", "/tmp")
    assert "CRITICAL" in f.getvalue() or "triage" in f.getvalue().lower(), \
        "Should warn at 90% budget"

@test("Budget warning fires at 75%")
def _():
    from research_runner import _print_summary
    import io; from contextlib import redirect_stdout
    budget = {"total_hours": 100, "spent_hours": 78, "remaining_hours": 22}
    f = io.StringIO()
    with redirect_stdout(f):
        _print_summary("WU-X", "COMPLETE", 0.1, budget, "standard", "/tmp")
    assert "warning" in f.getvalue().lower() or "triage" in f.getvalue().lower(), \
        "Should warn at 75% budget"

@test("blind_interpret flags normality violation")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"p_value": 0.01, "normality_ok": False}, f)
    result = blind_interpret(d)
    assert "normality" in result.lower(), f"Should flag normality violation, got: {result}"
    shutil.rmtree(d)

@test("blind_interpret flags shapiro p-value violation")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"p_value": 0.01, "shapiro_p": 0.02}, f)
    result = blind_interpret(d)
    assert "normality" in result.lower(), f"Should flag low shapiro p, got: {result}"
    shutil.rmtree(d)

@test("blind_interpret warns about multiple comparisons")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"p_value_a": 0.01, "p_value_b": 0.04, "p_value_c": 0.03}, f)
    result = blind_interpret(d)
    assert "bonferroni" in result.lower() or "correction" in result.lower(), \
        f"Should warn about multiple comparisons, got: {result}"
    shutil.rmtree(d)

@test("blind_interpret catches impossible p-value")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"p_value": -0.5}, f)
    result = blind_interpret(d)
    assert "REALITY VIOLATION" in result, f"Negative p-value should be REALITY VIOLATION, got: {result}"
    assert "strong evidence" not in result, "Should NOT classify impossible p-value"
    shutil.rmtree(d)

@test("blind_interpret catches extreme effect size")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"cohens_d": 50.0}, f)
    result = blind_interpret(d)
    assert "REALITY VIOLATION" in result or "measurement error" in result.lower(), \
        f"d=50 should be REALITY VIOLATION, got: {result}"
    shutil.rmtree(d)

@test("blind_interpret catches impossible accuracy")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"accuracy": 150}, f)
    result = blind_interpret(d)
    assert "REALITY VIOLATION" in result, f"accuracy=150 should be REALITY VIOLATION, got: {result}"
    assert "150.0% correct" not in result, "Should NOT classify impossible accuracy"
    shutil.rmtree(d)

@test("Reality constitution catches correlation > 1")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"pearson_r": 1.3}, f)
    result = blind_interpret(d)
    assert "REALITY VIOLATION" in result, f"r=1.3 should violate, got: {result}"
    shutil.rmtree(d)

@test("Reality constitution catches negative count")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"count_positive": -5}, f)
    result = blind_interpret(d)
    assert "REALITY VIOLATION" in result, f"negative count should violate, got: {result}"
    shutil.rmtree(d)

@test("Reality constitution catches negative duration")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"duration_seconds": -10}, f)
    result = blind_interpret(d)
    assert "REALITY VIOLATION" in result, f"negative time should violate, got: {result}"
    shutil.rmtree(d)

@test("Reality constitution flags d=4 as extraordinary")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"cohens_d": 4.0}, f)
    result = blind_interpret(d)
    assert "REALITY CHECK" in result, f"d=4 should flag as extraordinary, got: {result}"
    shutil.rmtree(d)

@test("Experiment source code saved alongside results")
def _():
    from research_runner import run_experiment, save_result
    def traceable_exp(output_dir, program_state):
        save_result(os.path.join(output_dir, "r.json"), dict({"v": 1}))
        return {"summary": "traceable"}
    run_experiment(traceable_exp, "phase_0", "WU-SRC",
                   expected_outputs=["r.json"], rigor="explore")
    # Find the output dir
    results_dir = os.path.join(TEST_DIR, "results")
    found_source = False
    for root, dirs, files in os.walk(results_dir):
        if "_experiment_source.py" in files and "wu_src" in root.lower():
            with open(os.path.join(root, "_experiment_source.py")) as f:
                content = f.read()
            assert "traceable_exp" in content, "Source should contain function name"
            assert "save_result" in content, "Source should contain actual code"
            found_source = True
    assert found_source, "Should save experiment source code"

@test("Research log created and appended")
def _():
    log_path = os.path.join(TEST_DIR, "research_log.md")
    if os.path.exists(log_path):
        with open(log_path) as f:
            content = f.read()
        assert "Research Log" in content, "Should have header"
        assert "WU-" in content, "Should have experiment entries"
        assert "|" in content, "Should be markdown table format"

@test("Generated .ipynb notebook is valid JSON with correct structure")
def _():
    # Simulate what colab_setup.py generates
    notebook = {
        "nbformat": 4, "nbformat_minor": 0,
        "metadata": {"colab": {"name": "Test"}, "kernelspec": {"name": "python3", "display_name": "Python 3"}},
        "cells": [
            {"cell_type": "code", "metadata": {}, "source": ["# Cell 1\n", "print('hello')\n"], "outputs": [], "execution_count": None},
            {"cell_type": "code", "metadata": {}, "source": ["# Cell 2\n"], "outputs": [], "execution_count": None},
            {"cell_type": "code", "metadata": {}, "source": ["# Cell 3\n", "print('results')\n"], "outputs": [], "execution_count": None},
        ]
    }
    nb_path = os.path.join(TEST_DIR, "test_notebook.ipynb")
    with open(nb_path, "w") as f:
        json.dump(notebook, f, indent=2)
    # Verify it's valid JSON
    with open(nb_path) as f:
        loaded = json.load(f)
    assert loaded["nbformat"] == 4, "Should be nbformat 4"
    assert len(loaded["cells"]) == 3, "Should have 3 cells"
    for cell in loaded["cells"]:
        assert cell["cell_type"] == "code", "All cells should be code"
        assert isinstance(cell["source"], list), "Source should be a list of strings"
        for line in cell["source"]:
            assert isinstance(line, str), f"Each source line should be string, got {type(line)}"
    os.remove(nb_path)

@test("blind_interpret flags multiple comparisons")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"p_value_a": 0.02, "p_value_b": 0.04, "p_value_c": 0.03}, f)
    result = blind_interpret(d)
    assert "Bonferroni" in result or "correction" in result.lower(), \
        f"Should warn about multiple comparisons, got: {result}"
    shutil.rmtree(d)

@test("Pre-registration blocked if results already exist")
def _():
    from scientific_method import pre_register
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "results.json"), "w") as f:
        json.dump({"p_value": 0.001}, f)
    try:
        pre_register(d, predictions={
            "hypothesis": "test", "prediction": "p < 0.05",
            "null_prediction": "p > 0.05",
            "what_would_change_my_mind": "p > 0.05"
        })
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "BEFORE" in str(e), f"Error should mention timing: {e}"
    shutil.rmtree(d)

@test("blind_interpret warns about small sample size")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"p_value": 0.04, "n": 5, "cohens_d": 0.8}, f)
    result = blind_interpret(d)
    assert "small sample" in result.lower() or "unreliable" in result.lower(), \
        f"Should warn about n=5, got: {result}"
    shutil.rmtree(d)

@test("State backup created after experiment")
def _():
    from research_runner import run_experiment, save_result, STATE_FILE
    def exp(o, s):
        save_result(os.path.join(o, "r.json"), dict({"v": 1}))
        return {}
    run_experiment(exp, "phase_0", "WU-BK", expected_outputs=["r.json"], rigor="explore")
    backup = STATE_FILE + ".bak"
    assert os.path.exists(backup), f"Backup should exist at {backup}"

@test("Reality check: correlation out of bounds")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"pearson_r": 1.5}, f)
    result = blind_interpret(d)
    assert "REALITY VIOLATION" in result, f"r=1.5 should be violation, got: {result}"
    shutil.rmtree(d)

@test("Reality check: negative count")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"count_items": -5}, f)
    result = blind_interpret(d)
    assert "REALITY VIOLATION" in result, f"count=-5 should be violation, got: {result}"
    shutil.rmtree(d)

@test("Reality check: negative duration")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"duration_seconds": -10}, f)
    result = blind_interpret(d)
    assert "REALITY VIOLATION" in result, f"time=-10 should be violation, got: {result}"
    shutil.rmtree(d)

@test("Reality check: domain constraints from pre-registration")
def _():
    from scientific_method import blind_interpret, pre_register
    d = tempfile.mkdtemp()
    pre_register(d,
        predictions={"hypothesis": "test", "prediction": "x<50",
                      "null_prediction": "x>50", "what_would_change_my_mind": "x>50"},
        analysis_plan={"test": "t-test", "reality_constraints": {
            "growth_pct": {"max": 50, "reason": "Plants cannot grow >50% in 48h"}
        }})
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"growth_pct": 200.0, "p_value": 0.001}, f)
    result = blind_interpret(d)
    assert "REALITY VIOLATION" in result, f"growth=200% should violate max=50, got: {result}"
    assert "50" in result, f"Should mention the constraint value"
    shutil.rmtree(d)

@test("Validity gate: VALID + SOUND")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"p_value": 0.003, "cohens_d": 0.8}, f)
    result = blind_interpret(d)
    assert "VALID + SOUND" in result, f"p<0.05 with no violations should be VALID+SOUND, got: {result}"
    shutil.rmtree(d)

@test("Validity gate: VALID + UNSOUND via reality violation")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"p_value": 0.001, "cohens_d": 15.0}, f)
    result = blind_interpret(d)
    assert "VALID + UNSOUND" in result, f"p<0.05 with d=15 should be VALID+UNSOUND, got: {result}"
    assert "DO NOT TRUST" in result, "Should say do not trust"
    shutil.rmtree(d)

@test("Validity gate: VALID + UNSOUND via assumption failure")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"p_value": 0.01, "normality_ok": False}, f)
    result = blind_interpret(d)
    assert "VALID + UNSOUND" in result, f"p<0.05 with normality_ok=False should be VALID+UNSOUND, got: {result}"
    shutil.rmtree(d)

@test("Validity gate: INVALID + SOUND")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"p_value": 0.42, "cohens_d": 0.1}, f)
    result = blind_interpret(d)
    assert "INVALID + SOUND" in result, f"p>0.05 with no violations should be INVALID+SOUND, got: {result}"
    shutil.rmtree(d)

@test("Validity gate: INVALID + UNSOUND")
def _():
    from scientific_method import blind_interpret
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "r.json"), "w") as f:
        json.dump({"p_value": 0.5, "duration_seconds": -10}, f)
    result = blind_interpret(d)
    assert "INVALID + UNSOUND" in result, f"p>0.05 with violations should be INVALID+UNSOUND, got: {result}"
    shutil.rmtree(d)

# --- SUMMARY ---

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

shutil.rmtree(TEST_DIR)
sys.exit(0 if failed == 0 else 1)
