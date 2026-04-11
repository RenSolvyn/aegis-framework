"""
Aegis Scientific Method Layer (v3)

Six tools that make solo research competitive with institutional work:
  1. pre_register()      — lock predictions before running experiments
  2. power_check()       — verify you have enough data to detect your effect
  3. devils_advocate()    — structured adversarial review of your results
  4. literature_check()   — document how your work connects to prior research
  5. replication_package()— bundle everything for reproducibility
  6. publication_check()  — readiness checklist before submission

Usage:
    from scientific_method import pre_register, power_check

    # Before running your experiment:
    pre_register(output_dir, predictions={
        "hypothesis": "Feature X is L3-positive",
        "prediction": "rho > 0.15",
        "null_prediction": "rho < adaptive_threshold",
        "what_would_change_my_mind": "rho < 0.05 with BF > 10"
    })

    # Before designing your experiment:
    n_needed = power_check(effect_size=0.5, alpha=0.05, power=0.80)
"""

import os
import json
import hashlib
import math
from datetime import datetime, timezone


# =====================================================================
# 0. QUESTION REFINEMENT — is this even the right question?
# =====================================================================

def question_refine(output_dir, raw_question):
    """
    Turn a raw curiosity into a testable research question.

    This is the FIRST step — before writing any code, before
    pre-registration, before anything. Most failed research starts
    with a bad question, not bad execution.

    Parameters
    ----------
    output_dir : str — where to save the refinement
    raw_question : str — the question exactly as the person asked it

    Returns
    -------
    filepath of the refinement template to fill in
    """
    template = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "NEEDS COMPLETION — answer every question below",
        "raw_question": raw_question,
        "refinement_steps": {
            "1_specificity": {
                "prompt": "Is this question specific enough to have a yes/no answer?",
                "example_bad": "Does diet affect health?",
                "example_good": "Do people who eat >5 servings of vegetables/day have lower blood pressure than those who eat <2?",
                "your_refined_question": "FILL IN",
            },
            "2_measurability": {
                "prompt": "What exactly will you measure, and how?",
                "example": "Blood pressure measured with a digital cuff, recorded as systolic/diastolic mmHg",
                "your_measurement": "FILL IN",
                "your_units": "FILL IN",
            },
            "3_data_availability": {
                "prompt": "Do you have (or can you get) the data needed to answer this?",
                "options": [
                    "I already have the data",
                    "I can collect it myself",
                    "Public dataset exists",
                    "I would need to create a study",
                ],
                "your_answer": "FILL IN",
                "where_is_the_data": "FILL IN",
            },
            "4_prior_work": {
                "prompt": "Has someone already answered this question?",
                "action": "Search Google Scholar for your question before proceeding",
                "search_url": "https://scholar.google.com",
                "what_you_found": "FILL IN",
                "how_yours_differs": "FILL IN",
            },
            "5_falsifiability": {
                "prompt": "What result would prove you WRONG?",
                "why_this_matters": "If nothing could change your mind, it's not research — it's belief.",
                "your_answer": "FILL IN",
            },
            "6_so_what": {
                "prompt": "If you find the answer, who cares? Why does it matter?",
                "your_answer": "FILL IN",
            },
            "7_feasibility": {
                "prompt": "Can you actually do this with your time, budget, and skills?",
                "estimated_time": "FILL IN",
                "estimated_cost": "FILL IN",
                "skills_needed": "FILL IN",
                "skills_you_have": "FILL IN",
            },
        },
        "final_research_question": "FILL IN after completing all steps above",
        "ready_to_proceed": False,
    }

    filepath = os.path.join(output_dir, "question_refinement.json")
    os.makedirs(output_dir, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(template, f, indent=2)

    print()
    print("  ┌─────────────────────────────────────────┐")
    print("  │  Question Refinement                    │")
    print("  ├─────────────────────────────────────────┤")
    print(f"  │  Your question:                         │")
    q = raw_question[:37]
    print(f"  │  {q:<37}  │")
    print("  │                                         │")
    print("  │  Before writing any code, answer the    │")
    print("  │  7 questions in the refinement file.    │")
    print("  │  Most failed research starts with a     │")
    print("  │  bad question, not bad execution.       │")
    print("  └─────────────────────────────────────────┘")
    print()
    print(f"  File: {filepath}")
    print()

    return filepath


# =====================================================================
# 1. PRE-REGISTRATION — lock predictions before experiments
# =====================================================================

def pre_register(output_dir, predictions, analysis_plan=None, state_path=None):
    """
    Write timestamped, hashed predictions BEFORE running an experiment.

    The hash proves you can't change your predictions after seeing results.
    Call this at the TOP of your experiment function, before any computation.

    Parameters
    ----------
    output_dir : str — where to save the pre-registration file
    predictions : dict with keys:
        - hypothesis: what you believe (plain English)
        - prediction: specific measurable outcome you expect
        - null_prediction: what you'd see if you're wrong
        - what_would_change_my_mind: the strongest possible disconfirmation
    analysis_plan : dict (optional but recommended) with keys:
        - data_cleaning: how you'll handle missing/outlier data
        - statistical_test: which test you'll use and why
        - exclusion_criteria: what data gets excluded, decided in advance
        - multiple_comparisons: how you'll correct for multiple tests
        - sample_size_justification: why your N is sufficient

    Returns
    -------
    dict with filepath and hash
    """
    required_keys = ["hypothesis", "prediction", "null_prediction",
                     "what_would_change_my_mind"]
    missing = [k for k in required_keys if k not in predictions]
    if missing:
        raise ValueError(
            f"Pre-registration missing required fields: {missing}\n"
            f"You must state what would change your mind BEFORE running."
        )

    # Guard: pre-registration must happen BEFORE results exist
    if os.path.exists(output_dir):
        existing_results = [f for f in os.listdir(output_dir)
                           if f.endswith('.json') and not f.startswith('_')
                           and f != 'pre_registration.json']
        if existing_results:
            raise RuntimeError(
                f"Results already exist in {output_dir}: {existing_results}\n"
                f"Pre-registration must happen BEFORE computation, not after.\n"
                f"If you need to re-run, use a fresh output directory."
            )

    registration = {
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "status": "PRE-REGISTERED (locked before experiment)",
        "predictions": predictions,
        "analysis_plan": analysis_plan or {},
        "has_analysis_plan": analysis_plan is not None,
    }

    if not analysis_plan:
        print("[pre-reg] Note: no analysis_plan provided.")
        print("[pre-reg] For publication-quality work, pre-register your")
        print("[pre-reg] analysis steps too — not just the hypothesis.")
        print("[pre-reg] See docs/CONCEPTS.md for why this matters.")

    # Serialize and hash — this proves the content wasn't modified
    content = json.dumps(registration, indent=2, sort_keys=True)
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    registration["integrity_hash"] = content_hash

    filepath = os.path.join(output_dir, "pre_registration.json")
    os.makedirs(output_dir, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(registration, f, indent=2)

    # Also write the hash separately for easy verification
    with open(filepath + ".sha256", "w") as f:
        f.write(content_hash)

    print(f"[pre-reg] Predictions locked: {filepath}")
    print(f"[pre-reg] Hash: {content_hash[:16]}...")
    print(f"[pre-reg] Hypothesis: {predictions['hypothesis']}")
    print(f"[pre-reg] What would change your mind: "
          f"{predictions['what_would_change_my_mind']}")

    return {"filepath": filepath, "hash": content_hash}


def verify_pre_registration(output_dir):
    """
    Verify that a pre-registration exists and hasn't been tampered with.
    Call this when reviewing results to confirm predictions were locked
    before the experiment ran.
    """
    filepath = os.path.join(output_dir, "pre_registration.json")
    if not os.path.exists(filepath):
        print("[pre-reg] WARNING: No pre-registration found.")
        print("[pre-reg] Results were NOT pre-registered.")
        return False

    with open(filepath, "r") as f:
        data = json.load(f)

    stored_hash = data.pop("integrity_hash", None)
    content = json.dumps(data, indent=2, sort_keys=True)
    computed_hash = hashlib.sha256(content.encode()).hexdigest()

    if stored_hash == computed_hash:
        print(f"[pre-reg] VERIFIED: predictions unchanged since registration")
        print(f"[pre-reg] Registered: {data.get('registered_at', 'unknown')}")
        return True
    else:
        print(f"[pre-reg] TAMPERED: predictions were modified after registration!")
        print(f"[pre-reg] Stored hash:   {stored_hash}")
        print(f"[pre-reg] Computed hash: {computed_hash}")
        return False


# =====================================================================
# 1b. BLIND INTERPRETATION — code-generated, no AI, no hypothesis
# =====================================================================

def blind_interpret(output_dir):
    """
    Mechanically interpret experiment results without knowing the
    hypothesis. This is CODE, not AI — it cannot be biased.

    Scans result files for common statistical values and classifies
    them in plain English. Also compares pre-registered predictions
    against observed results.

    Called automatically by Cell 3 of the Colab notebook.

    Returns
    -------
    str — plain-English interpretation, or empty string if no
          interpretable values found
    """
    lines = []

    # Load all result files
    results = {}
    if not os.path.exists(output_dir):
        return ""
    for fname in sorted(os.listdir(output_dir)):
        if fname.endswith('.json') and not fname.startswith('_') and fname != 'pre_registration.json':
            try:
                with open(os.path.join(output_dir, fname)) as f:
                    data = json.load(f)
                for k, v in data.items():
                    if not k.startswith('_') and isinstance(v, (int, float, bool, dict)):
                        results[k] = v
            except (json.JSONDecodeError, IOError):
                pass

    if not results:
        return ""

    lines.append("BLIND INTERPRETATION (code-generated, no AI, no hypothesis):")

    # ===== REALITY CONSTITUTION (code-enforced) =====
    # These are physical/mathematical laws that cannot be violated.
    # Any violation is a measurement error, bug, or confound — not a discovery.
    reality_violations = []

    for k, v in results.items():
        kl = k.lower()
        if isinstance(v, (int, float)) and not isinstance(v, bool):

            # PROBABILITY BOUNDS: must be [0, 1]
            if ('p_val' in kl or kl == 'p' or kl.endswith('_p')
                    or 'probability' in kl or 'prob_' in kl):
                if v < 0 or v > 1:
                    reality_violations.append(
                        f"  REALITY VIOLATION: {k} = {v} — probabilities must be between 0 and 1.")

            # CORRELATION BOUNDS: must be [-1, 1]
            elif ('correlation' in kl or kl.startswith('r_') or kl == 'rho'
                    or 'spearman' in kl or 'pearson' in kl or kl == 'r'):
                if v < -1 or v > 1:
                    reality_violations.append(
                        f"  REALITY VIOLATION: {k} = {v} — correlations must be between -1 and 1.")

            # R-SQUARED BOUNDS: must be [0, 1]
            elif 'r_squared' in kl or 'r2' in kl or kl == 'rsq':
                if v < 0 or v > 1:
                    reality_violations.append(
                        f"  REALITY VIOLATION: {k} = {v} — R-squared must be between 0 and 1.")

            # ACCURACY/PERCENTAGE BOUNDS: must be [0, 100] or [0, 1]
            elif 'accuracy' in kl or 'precision' in kl or 'recall' in kl or 'f1' in kl:
                if v < 0 or v > 100:
                    reality_violations.append(
                        f"  REALITY VIOLATION: {k} = {v} — accuracy cannot be negative or above 100%.")

            # PROPORTION/RATE BOUNDS: [0, 1] or [0, 100]
            elif ('rate' in kl or 'ratio' in kl or 'proportion' in kl
                    or 'percent' in kl or 'efficiency' in kl):
                if v < -1:
                    reality_violations.append(
                        f"  REALITY VIOLATION: {k} = {v} — rates/proportions cannot be deeply negative.")
                elif v > 1000:
                    reality_violations.append(
                        f"  REALITY CHECK: {k} = {v} — a {v:.0f}x rate/ratio is extraordinary. Verify this is not a unit error.")

            # NEGATIVE COUNTS: counts cannot be negative
            elif ('count' in kl or 'n_' in kl or kl == 'n'
                    or 'frequency' in kl or 'num_' in kl):
                if v < 0:
                    reality_violations.append(
                        f"  REALITY VIOLATION: {k} = {v} — counts cannot be negative.")

            # NEGATIVE DURATIONS: time cannot be negative
            elif 'time' in kl or 'duration' in kl or 'latency' in kl or 'seconds' in kl:
                if v < 0:
                    reality_violations.append(
                        f"  REALITY VIOLATION: {k} = {v} — time/duration cannot be negative.")

            # EFFECT SIZE THRESHOLDS (domain-calibrated)
            elif 'cohens_d' in kl or 'cohen_d' in kl or 'effect_size' in kl:
                if abs(v) > 10:
                    reality_violations.append(
                        f"  REALITY VIOLATION: {k} = {v} — effect size above 10 is almost certainly a measurement error.")
                elif abs(v) > 5:
                    reality_violations.append(
                        f"  REALITY CHECK: {k} = {v} — effect size above 5 is extraordinary in any field. Verify computation.")
                elif abs(v) > 3:
                    reality_violations.append(
                        f"  REALITY CHECK: {k} = {v} — effect size above 3 is very rare in behavioral/social science.")

            # EXTRAORDINARY MAGNITUDES: any value > 10000 deserves scrutiny
            elif abs(v) > 10000 and 'id' not in kl and 'seed' not in kl and 'step' not in kl:
                reality_violations.append(
                    f"  REALITY CHECK: {k} = {v} — very large magnitude. Verify units and computation.")

    # CROSS-VARIABLE CONSISTENCY CHECKS
    # Growth/change percentages > 500% are extraordinary
    for k, v in results.items():
        kl = k.lower()
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            if ('growth' in kl or 'change' in kl or 'gain' in kl or 'increase' in kl
                    or 'improvement' in kl) and ('pct' in kl or 'percent' in kl or '%' in k):
                if abs(v) > 500:
                    reality_violations.append(
                        f"  REALITY CHECK: {k} = {v}% — a {abs(v):.0f}% change is extraordinary. Verify this isn't a unit or baseline error.")

    # Output > Input check (conservation-like)
    input_val = None
    output_val = None
    for k, v in results.items():
        kl = k.lower()
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            if 'input' in kl or 'before' in kl or 'baseline' in kl or 'initial' in kl:
                input_val = (k, v)
            elif 'output' in kl or 'after' in kl or 'final' in kl:
                output_val = (k, v)
    if input_val and output_val:
        ratio = output_val[1] / input_val[1] if input_val[1] != 0 else float('inf')
        if ratio > 10:
            reality_violations.append(
                f"  REALITY CHECK: {output_val[0]}/{input_val[0]} ratio = {ratio:.1f}x — "
                f"a 10x+ output/input ratio is extraordinary. Check for unit mismatch or measurement error.")

    # Check for domain-specific constraints from pre-registration
    prereg_path = os.path.join(output_dir, "pre_registration.json")
    if os.path.exists(prereg_path):
        try:
            with open(prereg_path) as f:
                pr = json.load(f)
            constraints = pr.get("analysis_plan", {}).get("reality_constraints", {})
            for ck, cv in constraints.items():
                if ck in results and isinstance(results[ck], (int, float)) and not isinstance(results[ck], bool):
                    if isinstance(cv, dict):
                        if 'max' in cv and results[ck] > cv['max']:
                            reality_violations.append(
                                f"  REALITY VIOLATION: {ck} = {results[ck]} exceeds pre-registered maximum of {cv['max']}. {cv.get('reason', '')}")
                        if 'min' in cv and results[ck] < cv['min']:
                            reality_violations.append(
                                f"  REALITY VIOLATION: {ck} = {results[ck]} below pre-registered minimum of {cv['min']}. {cv.get('reason', '')}")
        except Exception:
            pass

    if reality_violations:
        for rv in reality_violations:
            lines.append(rv)
        lines.append("  Physical law > statistical significance. Check measurements before conclusions.")

    # Classify p-values
    for k, v in results.items():
        kl = k.lower()
        if 'p_val' in kl or kl == 'p' or kl.endswith('_p'):
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                continue
            if v < 0 or v > 1:
                continue  # already flagged as REALITY VIOLATION
            if v < 0.001:
                label = "very strong evidence against null (p < 0.001)"
            elif v < 0.01:
                label = "strong evidence against null (p < 0.01)"
            elif v < 0.05:
                label = "moderate evidence against null (p < 0.05)"
            elif v < 0.10:
                label = "weak evidence, not conventionally significant (p < 0.10)"
            else:
                label = "no significant evidence against null (p >= 0.10)"
            lines.append(f"  {k} = {v:.4f} → {label}")

    # Classify effect sizes (Cohen's d)
    for k, v in results.items():
        kl = k.lower()
        if 'cohens_d' in kl or 'cohen_d' in kl or 'effect_size' in kl:
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                continue
            if abs(v) > 10:
                continue  # already flagged as REALITY VIOLATION
            av = abs(v)
            if av < 0.2:
                label = "negligible effect"
            elif av < 0.5:
                label = "small effect"
            elif av < 0.8:
                label = "medium effect"
            else:
                label = "large effect"
            lines.append(f"  {k} = {v:.3f} → {label}")

    # Classify correlations
    for k, v in results.items():
        kl = k.lower()
        if 'correlation' in kl or kl.startswith('r_') or kl == 'rho' or 'spearman' in kl or 'pearson' in kl:
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                continue
            if abs(v) > 1:
                continue  # already flagged as REALITY VIOLATION
            av = abs(v)
            if av < 0.1:
                label = "negligible relationship"
            elif av < 0.3:
                label = "weak relationship"
            elif av < 0.5:
                label = "moderate relationship"
            elif av < 0.7:
                label = "strong relationship"
            else:
                label = "very strong relationship"
            direction = "positive" if v > 0 else "negative"
            lines.append(f"  {k} = {v:.3f} → {label} ({direction})")

    # Classify accuracy
    for k, v in results.items():
        kl = k.lower()
        if 'accuracy' in kl or 'acc' == kl:
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                continue
            if v < 0 or v > 100:
                continue  # already flagged as REALITY VIOLATION
            if v > 1:
                pct = v  # already percentage
            else:
                pct = v * 100
            lines.append(f"  {k} = {v} → {pct:.1f}% correct")

    # Flag anomalies
    for k, v in results.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            if math.isnan(v):
                lines.append(f"  WARNING: {k} is NaN (not a number — something went wrong)")
            elif math.isinf(v):
                lines.append(f"  WARNING: {k} is infinite (overflow — check your computation)")

    # Flag small sample sizes
    sample_keys = [k for k in results if k.lower() in ('n', 'n_obs', 'n_samples', 'sample_size', 'n_total')
                   or k.lower().startswith('n_')]
    for k in sample_keys:
        v = results[k]
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            if v < 20:
                lines.append(f"  WARNING: {k} = {int(v)} — very small sample. Results may be unreliable regardless of p-value.")
            elif v < 30:
                lines.append(f"  NOTE: {k} = {int(v)} — small sample. Consider whether assumptions (normality) hold.")

    # Flag assumption violations
    for k, v in results.items():
        kl = k.lower()
        if isinstance(v, dict) and 'normality_ok' in v:
            # Nested assumptions dict
            if v.get('normality_ok') is False:
                lines.append("  WARNING: normality assumption violated — statistical test may be inappropriate")
            if v.get('variance_ok') is False:
                lines.append("  WARNING: equal variance assumption violated — consider Welch's t-test")
        elif kl == 'normality_ok' and v is False:
            lines.append("  WARNING: normality assumption violated — consider non-parametric test")
        elif kl == 'variance_ok' and v is False:
            lines.append("  WARNING: equal variance assumption violated — consider Welch's t-test")
        elif ('normality' in kl or 'shapiro' in kl) and isinstance(v, (int, float)) and v < 0.05:
            lines.append(f"  WARNING: {k} = {v:.4f} — normality may be violated (p < 0.05)")
        elif 'levene' in kl and isinstance(v, (int, float)) and v < 0.05:
            lines.append(f"  WARNING: {k} = {v:.4f} — equal variance may be violated (p < 0.05)")

    # Multiple comparison warning
    p_count = sum(1 for k in results if 'p_val' in k.lower() or k.lower() == 'p' or k.lower().endswith('_p'))
    if p_count >= 3:
        corrected_alpha = round(0.05 / p_count, 4)
        lines.append(f"  NOTE: {p_count} p-values found. With Bonferroni correction,")
        lines.append(f"    significance threshold drops from 0.05 to {corrected_alpha}.")
        lines.append(f"    Check if your results survive this correction.")

    # Pre-registration comparison
    prereg_path = os.path.join(output_dir, "pre_registration.json")
    if os.path.exists(prereg_path):
        try:
            with open(prereg_path) as f:
                prereg = json.load(f)
            preds = prereg.get('predictions', {})
            # Verify integrity
            stored_hash = prereg.get('integrity_hash')
            if stored_hash:
                check_data = {k: v for k, v in prereg.items() if k != 'integrity_hash'}
                computed = hashlib.sha256(
                    json.dumps(check_data, indent=2, sort_keys=True).encode()
                ).hexdigest()
                if stored_hash == computed:
                    lines.append("  Pre-registration integrity: VERIFIED (not tampered)")
                else:
                    lines.append("  Pre-registration integrity: FAILED (predictions may have been changed!)")

            # Verify timing — pre-reg should exist before results
            prereg_time = os.path.getmtime(prereg_path)
            for fname in os.listdir(output_dir):
                if fname.endswith('.json') and not fname.startswith('_') and fname != 'pre_registration.json':
                    result_time = os.path.getmtime(os.path.join(output_dir, fname))
                    if result_time < prereg_time - 1:  # 1 second tolerance
                        lines.append("  WARNING: results file created BEFORE pre-registration — predictions may have been written after seeing data")
                        break
        except (json.JSONDecodeError, IOError):
            pass

    if len(lines) <= 1:
        return ""

    return "\n".join(lines)


# =====================================================================
# 2. POWER ANALYSIS — do you have enough data?
# =====================================================================

def power_check(effect_size, alpha=0.05, power=0.80, test="two_sample_t"):
    """
    Calculate minimum sample size needed to detect an effect.

    This prevents the most common research failure: running an experiment
    that was doomed to be inconclusive before it started.

    Parameters
    ----------
    effect_size : float — Cohen's d (0.2=small, 0.5=medium, 0.8=large)
    alpha : float — significance level (default 0.05)
    power : float — desired power (default 0.80 = 80% chance of detecting effect)
    test : str — "two_sample_t", "paired_t", "correlation", "proportion"

    Returns
    -------
    dict with n_per_group, total_n, and interpretation
    """
    if effect_size <= 0:
        raise ValueError("Effect size must be positive")

    # Using the normal approximation for sample size
    from math import ceil

    # Z-values for alpha and power
    z_alpha = _z_value(1 - alpha / 2)  # two-tailed
    z_beta = _z_value(power)

    if test == "two_sample_t":
        n_per_group = ceil(2 * ((z_alpha + z_beta) / effect_size) ** 2)
        total_n = n_per_group * 2
        desc = f"two-sample t-test, {n_per_group} per group"

    elif test == "paired_t":
        n_per_group = ceil(((z_alpha + z_beta) / effect_size) ** 2)
        total_n = n_per_group
        desc = f"paired t-test, {n_per_group} pairs"

    elif test == "correlation":
        # For testing r != 0, use Fisher's z transform approximation
        n_per_group = ceil(((z_alpha + z_beta) / effect_size) ** 2 + 3)
        total_n = n_per_group
        desc = f"correlation test, {n_per_group} observations"

    elif test == "proportion":
        n_per_group = ceil(2 * ((z_alpha + z_beta) / effect_size) ** 2)
        total_n = n_per_group * 2
        desc = f"proportion test, {n_per_group} per group"

    else:
        raise ValueError(f"Unknown test type: {test}. "
                         f"Use: two_sample_t, paired_t, correlation, proportion")

    result = {
        "test": test,
        "effect_size": effect_size,
        "alpha": alpha,
        "power": power,
        "n_per_group": n_per_group,
        "total_n": total_n,
        "description": desc,
    }

    # Interpretation
    if effect_size < 0.2:
        size_label = "very small"
    elif effect_size < 0.5:
        size_label = "small"
    elif effect_size < 0.8:
        size_label = "medium"
    else:
        size_label = "large"

    print(f"[power] Effect size: {effect_size} ({size_label})")
    print(f"[power] Test: {test}")
    print(f"[power] Required: {desc}")
    print(f"[power] At alpha={alpha}, power={power}")
    print(f"[power]")
    print(f"[power] If you have fewer than {total_n} samples,")
    print(f"[power] a negative result may just mean not enough data.")

    return result


def _z_value(p):
    """Approximate inverse normal CDF (Abramowitz & Stegun)."""
    if p <= 0 or p >= 1:
        raise ValueError(f"p must be between 0 and 1, got {p}")
    if p < 0.5:
        return -_z_value(1 - p)
    t = math.sqrt(-2 * math.log(1 - p))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1 * t + c2 * t * t) / (1 + d1 * t + d2 * t * t + d3 * t * t * t)


# =====================================================================
# 3. DEVIL'S ADVOCATE — structured adversarial review
# =====================================================================

def devils_advocate(output_dir, results_summary):
    """
    Generate a structured adversarial review of your results.

    Call this AFTER getting results but BEFORE interpreting them.
    Forces you to actively try to disprove your own findings.

    Parameters
    ----------
    output_dir : str — where to save the review
    results_summary : dict with keys:
        - result: what you observed (plain English)
        - effect_size: measured effect size
        - p_value: if applicable
        - sample_size: how many data points

    Returns
    -------
    filepath of the adversarial review template to fill in
    """
    template = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "NEEDS COMPLETION — fill in all fields below",
        "your_result": results_summary,
        "adversarial_questions": {
            "alternative_explanations": [
                "What else could explain this result besides your hypothesis?",
                "YOUR ANSWER: (fill this in)",
            ],
            "confounds": [
                "What variables did you NOT control for?",
                "YOUR ANSWER: (fill this in)",
            ],
            "selection_bias": [
                "Did you choose to analyze this subset because it looked promising?",
                "YOUR ANSWER: (fill this in)",
            ],
            "measurement_validity": [
                "Does your metric actually measure what you think it measures?",
                "YOUR ANSWER: (fill this in)",
            ],
            "base_rate": [
                "How often would you see this result by chance? Did you check?",
                "YOUR ANSWER: (fill this in)",
            ],
            "strongest_objection": [
                "A skeptical reviewer's first objection would be:",
                "YOUR ANSWER: (fill this in)",
            ],
            "replication_prediction": [
                "If someone else ran this exact experiment, would they get the same result?",
                "YOUR ANSWER: (fill this in)",
            ],
        },
        "verdict_options": {
            "A": "Result survives adversarial review — proceed with confidence",
            "B": "Result has caveats — proceed but document limitations",
            "C": "Result doesn't survive — need additional experiments",
            "D": "Result is likely an artifact — do not proceed",
        },
        "your_verdict": "FILL IN: A, B, C, or D",
    }

    filepath = os.path.join(output_dir, "devils_advocate.json")
    os.makedirs(output_dir, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(template, f, indent=2)

    print(f"[advocate] Adversarial review template created: {filepath}")
    print(f"[advocate] FILL IN all 'YOUR ANSWER' fields before proceeding.")
    print(f"[advocate] The hardest question: what's your strongest objection?")

    return filepath


# =====================================================================
# 4. LITERATURE CONNECTION — how does this relate to prior work?
# =====================================================================

def literature_check(output_dir, your_finding, search_terms=None):
    """
    Create a structured template for connecting results to prior work.

    Parameters
    ----------
    output_dir : str
    your_finding : str — one-sentence summary of your result
    search_terms : list[str] — suggested search terms for finding related work
    """
    template = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "your_finding": your_finding,
        "status": "NEEDS COMPLETION",
        "suggested_search_terms": search_terms or ["(add your search terms)"],
        "search_locations": [
            "Google Scholar (scholar.google.com)",
            "Semantic Scholar (semanticscholar.org)",
            "arXiv (arxiv.org)",
            "Connected Papers (connectedpapers.com) — visual citation graph",
        ],
        "prior_work": [
            {
                "citation": "(Author, Year, Title)",
                "what_they_found": "(their main result)",
                "how_yours_differs": "(what's new in your work)",
                "does_it_support_or_contradict": "(support / contradict / extend)",
            },
        ],
        "questions_to_answer": [
            "Has anyone already answered this exact question?",
            "What's the closest prior work and how does yours extend it?",
            "Does your result contradict any published findings?",
            "What would someone working on this topic want to know about your work?",
            "Are there methods from prior work you should have used?",
        ],
        "your_positioning": "FILL IN: One paragraph on how your work fits into the field",
    }

    filepath = os.path.join(output_dir, "literature_connection.json")
    os.makedirs(output_dir, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(template, f, indent=2)

    print(f"[literature] Connection template created: {filepath}")
    print(f"[literature] Search for related work before claiming novelty.")

    return filepath


# =====================================================================
# 5. REPLICATION PACKAGE — can someone else reproduce this?
# =====================================================================

def replication_package(project_dir, output_path, work_units=None):
    """
    Bundle everything needed to reproduce your results.

    Creates a manifest listing every file, script, and state snapshot
    needed to replicate the experiment from scratch.

    Parameters
    ----------
    project_dir : str — your project root
    output_path : str — where to save the replication manifest
    work_units : list[str] — which work units to include (None = all)
    """
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_dir": project_dir,
        "framework": "aegis-v4.0",
        "contents": {
            "scripts": [],
            "state_snapshots": [],
            "outputs": [],
            "data_files": [],
            "dependencies": [],
        },
        "reproduction_steps": [],
    }

    # Scan for scripts
    scripts_dir = os.path.join(project_dir, "scripts")
    if os.path.exists(scripts_dir):
        for root, dirs, files in os.walk(scripts_dir):
            for f in sorted(files):
                if f.endswith(".py"):
                    path = os.path.join(root, f)
                    rel_path = os.path.relpath(path, project_dir)
                    size = os.path.getsize(path)
                    manifest["contents"]["scripts"].append({
                        "path": rel_path,
                        "size_bytes": size,
                    })

    # Check for program_state.json
    state_path = os.path.join(project_dir, "program_state.json")
    if os.path.exists(state_path):
        with open(state_path, "r") as f:
            state = json.load(f)
        manifest["contents"]["state_snapshots"].append({
            "path": "program_state.json",
            "last_session": state.get("last_session", 0),
            "last_work_unit": state.get("last_work_unit"),
        })

    # Scan for result files
    results_dir = os.path.join(project_dir, "results")
    if os.path.exists(results_dir):
        for root, dirs, files in os.walk(results_dir):
            for f in sorted(files):
                if f.endswith(".json") and not f.startswith("_"):
                    path = os.path.join(root, f)
                    rel_path = os.path.relpath(path, project_dir)
                    has_sha = os.path.exists(path + ".sha256")
                    manifest["contents"]["outputs"].append({
                        "path": rel_path,
                        "sha256_verified": has_sha,
                    })

    # Check for requirements
    req_path = os.path.join(project_dir, "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r") as f:
            deps = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        manifest["contents"]["dependencies"] = deps

    # Generate reproduction steps
    scripts = manifest["contents"]["scripts"]
    manifest["reproduction_steps"] = [
        "1. Clone this repository",
        "2. Install dependencies: pip install -r requirements.txt" if manifest["contents"]["dependencies"] else "2. Install dependencies: pip install numpy",
        "3. Set RESEARCH_DRIVE_ROOT to the project directory",
        f"4. Run scripts in order: {', '.join(s['path'] for s in scripts[:5])}",
        "5. Verify outputs match the SHA-256 checksums in the results/ directory",
    ]

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)

    n_scripts = len(manifest["contents"]["scripts"])
    n_outputs = len(manifest["contents"]["outputs"])
    verified = sum(1 for o in manifest["contents"]["outputs"] if o["sha256_verified"])

    print(f"[replication] Package manifest created: {output_path}")
    print(f"[replication] Scripts: {n_scripts}")
    print(f"[replication] Output files: {n_outputs} ({verified} SHA-verified)")
    print(f"[replication] A reviewer can follow the reproduction steps to verify.")

    return manifest


# =====================================================================
# 6. PUBLICATION READINESS — are you ready for peer review?
# =====================================================================

def publication_check(project_dir, verbose=True):
    """
    Check your project against publication standards.

    Returns a checklist with PASS/FAIL for each criterion.
    Run this before submitting to any venue.
    """
    checks = []

    def check(name, passed, detail=""):
        checks.append({"name": name, "passed": passed, "detail": detail})
        if verbose:
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))

    print()
    print("=" * 54)
    print("  Publication readiness check")
    print("=" * 54)
    print()

    # 1. Pre-registration exists
    results_dir = os.path.join(project_dir, "results")
    has_prereg = False
    if os.path.exists(results_dir):
        for root, dirs, files in os.walk(results_dir):
            if "pre_registration.json" in files:
                has_prereg = True
                break
    check("Pre-registered predictions",
          has_prereg,
          "predictions locked before experiments" if has_prereg else "no pre-registration found")

    # 1b. Analysis plan in pre-registration
    has_analysis_plan = False
    if has_prereg and os.path.exists(results_dir):
        for root, dirs, files in os.walk(results_dir):
            if "pre_registration.json" in files:
                try:
                    with open(os.path.join(root, "pre_registration.json")) as f:
                        prereg = json.load(f)
                    has_analysis_plan = prereg.get("has_analysis_plan", False)
                except Exception:
                    pass
                break
    check("Analysis plan pre-registered",
          has_analysis_plan,
          "analysis steps locked with predictions" if has_analysis_plan
          else "add analysis_plan to pre_register() for full rigor")

    # 1c. Question refinement completed
    has_refinement = False
    if os.path.exists(results_dir):
        for root, dirs, files in os.walk(results_dir):
            if "question_refinement.json" in files:
                has_refinement = True
                break
    # Also check docs/
    if not has_refinement:
        docs_dir = os.path.join(project_dir, "docs")
        if os.path.exists(docs_dir):
            for f in os.listdir(docs_dir):
                if "question" in f.lower() and "refin" in f.lower():
                    has_refinement = True
                    break
    check("Question refinement completed",
          has_refinement,
          "question vetted before experiments" if has_refinement
          else "run question_refine() to vet your research question")

    # 2. Research plan exists
    plan_path = os.path.join(project_dir, "docs", "research_plan.md")
    has_plan = os.path.exists(plan_path)
    check("Research plan documented",
          has_plan,
          "docs/research_plan.md exists" if has_plan else "create docs/research_plan.md")

    # 3. Multiple sessions completed
    state_path = os.path.join(project_dir, "program_state.json")
    sessions = 0
    if os.path.exists(state_path):
        with open(state_path, "r") as f:
            state = json.load(f)
        sessions = state.get("last_session", 0)
    check("Multiple experiments run",
          sessions >= 3,
          f"{sessions} sessions completed")

    # 4. Output verification
    verified_count = 0
    total_outputs = 0
    if os.path.exists(results_dir):
        for root, dirs, files in os.walk(results_dir):
            for f in files:
                if f.endswith(".json") and not f.startswith("_"):
                    total_outputs += 1
                    if os.path.exists(os.path.join(root, f + ".sha256")):
                        verified_count += 1
    check("Outputs SHA-verified",
          verified_count > 0 and verified_count == total_outputs,
          f"{verified_count}/{total_outputs} files verified")

    # 5. Error log exists
    log_path = os.path.join(project_dir, "logs", "error_log.md")
    has_log = os.path.exists(log_path)
    check("Error log maintained",
          has_log,
          "logs/error_log.md exists" if has_log else "no error log found")

    # 6. Devil's advocate completed
    has_advocate = False
    if os.path.exists(results_dir):
        for root, dirs, files in os.walk(results_dir):
            if "devils_advocate.json" in files:
                has_advocate = True
                break
    check("Adversarial review completed",
          has_advocate,
          "devil's advocate exists" if has_advocate else "run devils_advocate() on your results")

    # 7. Literature connection exists
    has_lit = False
    if os.path.exists(results_dir):
        for root, dirs, files in os.walk(results_dir):
            if "literature_connection.json" in files:
                has_lit = True
                break
    check("Literature connection documented",
          has_lit,
          "connection documented" if has_lit else "run literature_check() before publishing")

    # 8. Kill criteria defined
    has_kill = False
    if has_plan:
        with open(plan_path, "r") as f:
            plan_content = f.read().lower()
        has_kill = "kill" in plan_content or "stop" in plan_content or "pivot" in plan_content
    check("Kill criteria defined",
          has_kill,
          "stopping rules in research plan" if has_kill else "add kill criteria to research_plan.md")

    # 9+. Custom checks from extensions
    try:
        from extensions import get_custom_publication_checks
        custom = get_custom_publication_checks(project_dir)
        for name, passed_flag, detail in custom:
            check(name, passed_flag, detail)
    except ImportError:
        pass

    # Summary
    passed = sum(1 for c in checks if c["passed"])
    total = len(checks)
    print()
    print(f"  Score: {passed}/{total}")
    if passed == total:
        print(f"  READY for submission.")
    elif passed >= total - 2:
        print(f"  ALMOST ready — address the failures above.")
    else:
        print(f"  NOT ready — {total - passed} items need attention.")
    print()
    print("=" * 54)

    return {"passed": passed, "total": total, "checks": checks}
