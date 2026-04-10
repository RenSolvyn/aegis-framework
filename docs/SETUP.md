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


## 3. Add the framework (5 min)

Copy into your repo folder:
```
my-research/
├── src/
│   ├── research_runner.py    ← from this repo
│   └── git_sync.py           ← from this repo (optional)
├── scripts/
│   ├── phase_0/
│   └── phase_1/
├── results/summaries/
├── program_state.json        ← from templates/, fill in your details
└── .gitignore
```

Edit `program_state.json`: set your program name and total budget hours.

If using `git_sync.py`: edit `REPO_NAME` and `GITHUB_USER` at the top.

In GitHub Desktop: type "Initial setup" → Commit → Push origin. Done.


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

### Using GitHub Desktop (no command line)
1. Open GitHub Desktop → Fetch origin
2. Do your research (write script, review, run on Colab)
3. Save script to `scripts/` folder
4. Copy program_state.json from Drive after Colab run
5. GitHub Desktop → write summary → Commit → Push

### Using auto-commit from Colab (no GitHub Desktop needed)
1. Open Colab → run Cell 1 (mounts Drive, shows dashboard, pulls git)
2. Run Cell 2 (your experiment)
3. Runner auto-commits to GitHub
4. Close Colab


## Syncing between machines

Always Fetch/Pull before starting. Always Push when done.
If you use auto-commit, Colab pushes for you — just Pull on your
other machine before starting a new session there.
