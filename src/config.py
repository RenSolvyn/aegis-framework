"""
Aegis Configuration — single source of truth for all paths and settings.

Every other module imports from here. To configure Aegis for your
environment, set the RESEARCH_DRIVE_ROOT environment variable or
edit the defaults below.
"""

import os

# The root directory where your research project lives.
# On Colab: /content/drive/MyDrive/Research
# Locally: the project folder (or "." if running from within it)
DRIVE_ROOT = os.environ.get(
    "RESEARCH_DRIVE_ROOT",
    "/content/drive/MyDrive/Research"
)

# Derived paths — don't edit these, edit DRIVE_ROOT instead
STATE_FILE = os.path.join(DRIVE_ROOT, "program_state.json")
ERROR_LOG = os.path.join(DRIVE_ROOT, "logs", "error_log.md")
RESULTS_ROOT = os.path.join(DRIVE_ROOT, "results")
SCRIPTS_DIR = os.path.join(DRIVE_ROOT, "scripts")
SRC_DIR = os.path.join(DRIVE_ROOT, "src")

# Framework version
VERSION = "4.0.0"
