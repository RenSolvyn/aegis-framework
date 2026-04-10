"""
Git Sync — auto-commit to GitHub from Colab.

All configuration via environment variables — no hardcoded usernames or repos.

Setup once:
  1. Store these as Colab secrets:
     - GITHUB_TOKEN: your personal access token
     - GITHUB_USER: your GitHub username
     - GITHUB_REPO: your private repo name
  2. Call git_setup() in your first Colab cell

The runner calls git_sync() automatically after each experiment.
"""

import os
import subprocess

try:
    from config import DRIVE_ROOT
except ImportError:
    DRIVE_ROOT = os.environ.get("RESEARCH_DRIVE_ROOT", "/content/drive/MyDrive/Research")

REPO_LOCAL = "/content/repo"


def _run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"[git-sync] Failed: {cmd}\n{result.stderr}")
    return result


def _get_credentials():
    """Load credentials from Colab secrets or environment variables."""
    token = os.environ.get("GITHUB_TOKEN")
    user = os.environ.get("GITHUB_USER")
    repo = os.environ.get("GITHUB_REPO")

    # Try Colab secrets if env vars not set
    if not all([token, user, repo]):
        try:
            from google.colab import userdata
            token = token or userdata.get("GITHUB_TOKEN")
            user = user or userdata.get("GITHUB_USER")
            repo = repo or userdata.get("GITHUB_REPO")
        except Exception:
            pass

    if not token:
        print("[git-sync] No GITHUB_TOKEN found. Set it as a Colab secret or env var.")
        return None
    if not user:
        print("[git-sync] No GITHUB_USER found. Set it as a Colab secret or env var.")
        return None
    if not repo:
        print("[git-sync] No GITHUB_REPO found. Set it as a Colab secret or env var.")
        return None

    return {"token": token, "user": user, "repo": repo}


def git_setup():
    """Clone/pull repo. Call once per Colab session after Drive mount."""
    creds = _get_credentials()
    if not creds:
        return False

    repo_url = f"https://{creds['user']}:{creds['token']}@github.com/{creds['user']}/{creds['repo']}.git"

    if os.path.exists(REPO_LOCAL):
        _run(f"cd {REPO_LOCAL} && git pull origin main")
        print(f"[git-sync] Pulled latest")
    else:
        _run(f"git clone {repo_url} {REPO_LOCAL}")
        print(f"[git-sync] Cloned {creds['repo']}")

    _run(f'cd {REPO_LOCAL} && git config user.name "{creds["user"]}"')
    _run(f'cd {REPO_LOCAL} && git config user.email "{creds["user"]}@users.noreply.github.com"')
    return True


def git_sync(work_unit, phase, status, runtime_hours, summary=""):
    """Copy state + scripts from Drive to repo, commit, push."""
    if not os.path.exists(REPO_LOCAL):
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
        for root, dirs, files in os.walk(drive_scripts):
            for f in files:
                if f.endswith(".py"):
                    rel = os.path.relpath(root, drive_scripts)
                    dest_dir = os.path.join(REPO_LOCAL, "scripts", rel)
                    os.makedirs(dest_dir, exist_ok=True)
                    subprocess.run(["cp", os.path.join(root, f),
                                    os.path.join(dest_dir, f)])

    # Commit + push
    _run(f"cd {REPO_LOCAL} && git add -A")
    result = _run(f"cd {REPO_LOCAL} && git status --porcelain", check=False)
    if not result.stdout.strip():
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
