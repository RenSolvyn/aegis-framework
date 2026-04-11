# Setup Guide

Everything you need to go from zero to running. Pick your path:

- **Never used GitHub?** Start at Section 1
- **Comfortable with git?** Skip to Section 3
- **Want auto-commit from Colab?** Section 4


## 1. GitHub account + GitHub Desktop (10 min)

1. Go to **github.com/signup**. Create an account.
2. Enable two-factor auth: Settings → Password and authentication
3. Download **GitHub Desktop** from desktop.github.com. Install. Sign in.

GitHub Desktop replaces the command line. You never need Terminal.


## 2. Create your repository (5 min)

Go to **github.com/new**:
- Name: `my-research`
- **Private**
- Check "Add a README"
- Create

In GitHub Desktop → Clone a Repository → select yours → choose a local folder.

**Important:** Settings → Copilot → disable "use my code for Copilot."


## 3. Add the framework (2 min)

The easiest way: run the Colab setup (see README Step 1). It
downloads everything to your Google Drive automatically.

If you prefer local setup, use `bootstrap.py`:
```bash
python bootstrap.py
```

This creates the project structure with all source files.

To connect your local project to GitHub:
```bash
cd my-research
git init
git remote add origin https://github.com/YOUR_USER/my-research.git
git add .
git commit -m "Initial setup"
git push -u origin main
```


## 4. Auto-commit from Colab (optional, 5 min)

### Create a GitHub token
github.com → Settings → Developer settings → Personal access tokens → Tokens (classic):
- Note: `colab`
- Expiration: 90 days
- Scopes: `repo` and `workflow`
- Generate → copy the token

### Store in Colab
Colab → 🔑 sidebar → Add three secrets:
- `GITHUB_TOKEN` → paste your token
- `GITHUB_USER` → your GitHub username
- `GITHUB_REPO` → your private repo name
- Toggle "Notebook access" ON for all three

### How it works
The runner auto-calls git_sync() after every experiment. It reads
your credentials from Colab secrets, copies program_state.json and
scripts from Drive to the repo, commits, and pushes. You never
run git commands manually.

If credentials aren't set, git sync is silently skipped — your
experiment still runs and results still save to Drive.


## 5. Your .gitignore

```
*.pt
*.npz
*.bin
*.safetensors
results/raw/
models/
__pycache__/
*.pyc
.env
.DS_Store
*.tmp
```

Git tracks scripts and state (small, text). Drive tracks data and
weights (large, binary).


## Daily workflow

### Using Colab (recommended)
1. Open your Aegis notebook on Drive
2. Run Cell 1 (connects Drive, shows dashboard)
3. Paste experiment script into Cell 2, use Runtime → Run all
4. Copy Cell 3 results back to your AI for interpretation

### Using auto-commit from Colab (optional)
The runner auto-calls git_sync() after every experiment if
credentials are configured. It pushes program_state.json and
results to GitHub. If credentials aren't set, git sync is
silently skipped — your experiment still runs and results
still save to Drive.


## Syncing between machines

Always Fetch/Pull before starting. Always Push when done.
If you use auto-commit, Colab pushes for you — just Pull on your
other machine before starting a new session there.
