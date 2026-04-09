"""
Git Sync — auto-commit to GitHub from Colab.

Setup once:
  1. Store GITHUB_TOKEN as a Colab secret
  2. Set REPO_NAME and GITHUB_USER below
  3. Call git_setup() in your first Colab cell

The runner calls git_sync() automatically after each experiment.
"""

import os
import subprocess

REPO_NAME = "my-research"
GITHUB_USER = "YOUR-USERNAME"
REPO_LOCAL = "/content/repo"
DRIVE_ROOT = os.environ.get("RESEARCH_DRIVE_ROOT", "/content/drive/MyDrive/Research")


def _run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"[git-sync] Failed: {cmd}\n{result.stderr}")
    return result


def git_setup():
    """Clone/pull repo. Call once per Colab session after Drive mount."""
    try:
        from google.colab import userdata
        token = userdata.get("GITHUB_TOKEN")
    except Exception:
        print("[git-sync] No GITHUB_TOKEN in Colab secrets. Skipping git.")
        return False

    repo_url = f"https://{GITHUB_USER}:{token}@github.com/{GITHUB_USER}/{REPO_NAME}.git"

    if os.path.exists(REPO_LOCAL):
        _run(f"cd {REPO_LOCAL} && git pull origin main")
        print(f"[git-sync] Pulled latest")
    else:
        _run(f"git clone {repo_url} {REPO_LOCAL}")
        print(f"[git-sync] Cloned {REPO_NAME}")

    _run(f'cd {REPO_LOCAL} && git config user.name "{GITHUB_USER}"')
    _run(f'cd {REPO_LOCAL} && git config user.email "{GITHUB_USER}@users.noreply.github.com"')
    return True


def git_sync(work_unit, phase, status, runtime_hours, summary=""):
    """Copy state + scripts from Drive to repo, commit, push."""
    if not os.path.exists(REPO_LOCAL):
        print("[git-sync] Repo not cloned. Call git_setup() first.")
        return False

    # Sync program_state.json
    src = os.path.join(DRIVE_ROOT, "program_state.json")
    dst = os.path.join(REPO_LOCAL, "program_state.json")
    if os.path.exists(src):
        subprocess.run(["cp", src, dst])

    # Sync scripts
    repo_scripts = os.path.join(REPO_LOCAL, "scripts", phase)
    os.makedirs(repo_scripts, exist_ok=True)
    drive_scripts = os.path.join(DRIVE_ROOT, "scripts")
    if os.path.exists(drive_scripts):
        for f in os.listdir(drive_scripts):
            if f.endswith(".py"):
                subprocess.run(["cp", os.path.join(drive_scripts, f), repo_scripts])

    # Commit + push
    _run(f"cd {REPO_LOCAL} && git add -A")
    result = _run(f"cd {REPO_LOCAL} && git status --porcelain", check=False)
    if not result.stdout.strip():
        print("[git-sync] Nothing to commit")
        return True

    msg = f"{work_unit} {status.lower()}"
    if summary:
        msg += f": {summary}"
    msg += f"\n\nRuntime: {runtime_hours:.2f} hrs | Phase: {phase}"

    _run(f'cd {REPO_LOCAL} && git commit -m "{msg}"')
    push = _run(f"cd {REPO_LOCAL} && git push origin main")

    if push.returncode == 0:
        print(f"[git-sync] Pushed: {work_unit} {status}")
    else:
        print(f"[git-sync] Push failed — will retry next session")
    return push.returncode == 0
