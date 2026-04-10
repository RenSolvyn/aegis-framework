"""
Aegis Extensions — add custom checks without editing framework source.

Create a file called `extensions.py` in your project's src/ folder.
Define any of the hook functions below. The runner calls them automatically
at the right time.

Example extensions.py:
    def on_experiment_start(work_unit, phase, program_state):
        '''Called before every experiment runs.'''
        # Check custom prerequisites
        if phase == "phase_1" and "calibration_complete" not in program_state.get("flags", {}):
            raise RuntimeError("Run calibration before phase_1 experiments")

    def on_experiment_end(work_unit, status, results, program_state):
        '''Called after every experiment completes.'''
        # Custom logging
        if status == "COMPLETE":
            print(f"  [custom] {work_unit} done — sending notification")

    def on_save_result(filepath, data):
        '''Called after every save_result().'''
        # Custom validation
        for key, val in data.items():
            if key.startswith("_"):
                continue
            if isinstance(val, float) and (val != val):  # NaN check
                raise ValueError(f"NaN detected in result field '{key}'")

    def custom_publication_checks(project_dir):
        '''Called by publication_check() — return list of (name, passed, detail).'''
        checks = []
        # Example: verify a specific file exists
        import os
        has_ethics = os.path.exists(os.path.join(project_dir, "docs", "ethics.md"))
        checks.append(("Ethics review documented", has_ethics,
                       "docs/ethics.md exists" if has_ethics else "create docs/ethics.md"))
        return checks
"""

import os
import sys
import importlib
import importlib.util


_extensions = None
_load_attempted = False


def _load_extensions():
    """Try to load user extensions. Silent if none exist."""
    global _extensions, _load_attempted
    if _load_attempted:
        return _extensions
    _load_attempted = True

    try:
        from config import SRC_DIR
    except ImportError:
        SRC_DIR = os.environ.get("RESEARCH_DRIVE_ROOT", ".")
        SRC_DIR = os.path.join(SRC_DIR, "src")

    ext_path = os.path.join(SRC_DIR, "extensions.py")
    if not os.path.exists(ext_path):
        return None

    try:
        spec = importlib.util.spec_from_file_location("extensions", ext_path)
        _extensions = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_extensions)
        return _extensions
    except Exception as e:
        print(f"[extensions] Warning: could not load extensions.py: {e}")
        return None


def call_hook(hook_name, *args, **kwargs):
    """
    Call a user-defined hook if it exists. Silent if not defined.
    Returns the hook's return value, or None if no hook exists.
    """
    ext = _load_extensions()
    if ext is None:
        return None
    hook = getattr(ext, hook_name, None)
    if hook is None:
        return None
    try:
        return hook(*args, **kwargs)
    except Exception as e:
        print(f"[extensions] Hook '{hook_name}' raised: {e}")
        raise


def get_custom_publication_checks(project_dir):
    """Get custom publication checks if defined."""
    ext = _load_extensions()
    if ext is None:
        return []
    fn = getattr(ext, "custom_publication_checks", None)
    if fn is None:
        return []
    try:
        return fn(project_dir)
    except Exception as e:
        print(f"[extensions] custom_publication_checks raised: {e}")
        return []
