# GitHub Push Setup for Morning Briefing

## Overview

The 九九 morning briefing cron job can push reports to a GitHub Pages site for persistent archiving and public access.

Two patterns exist:

### Pattern A: Dedicated repo (jiujiu-daily)
A standalone GitHub repo `corinwe/jiujiu-daily` — stores only the daily morning report as `YYYY-MM-DD.md` plus minimal static site files via `build.py`.

### Pattern B: Multi-function repo (ai-morning-report-site)
An existing repo that already has report infrastructure (`reports/`, `build.py`, `^C templates`).

For boss's setup: Pattern A was chosen (`jiujiu-daily`).

---

## Setup Steps

### 1. Install GitHub CLI
```bash
apt-get install gh -y
```

### 2. Authenticate with Token
```bash
gh auth login --with-token < ~/gh_token.txt
# Or pipe: echo "$GITHUB_TOKEN" | gh auth login --with-token
```

Personal Access Token needs `repo` scope (full control of private repositories).

### 3. Create Repository
```bash
gh repo create corinwe/jiujiu-daily --public --description "九九每日财富投资晨报" --add-readme
```

### 4. Clone + Init
```bash
git clone git@github.com:corinwe/jiujiu-daily.git ~/jiujiu-daily
cd ~/jiujiu-daily
# Create reports/ directory for daily reports
mkdir -p reports
```

### 5. Build.py (TTS + Static Site)
The repo has a `build.py` that:
- Reads Markdown from `reports/` directory
- Extracts metadata (date, word count, sections, highlights)
- Generates TTS audio via `edge-tts` for reports missing audio
- Injects data into HTML templates → builds `index.html` + `report.html`

Run it after adding a new report:
```bash
cd ~/jiujiu-daily && python3 build.py
```

---

## Cron Job Integration

The Hermes cron job uses two modes:

### Mode 1: Cron script (`script:` field)
Define a shell script in `~/.hermes/scripts/` that:
1. Captures the agent's generated report Markdown to `reports/YYYY-MM-DD.md`
2. Runs `build.py` (if present)
3. Git commit + push to origin/main

### Mode 2: Agent-generated output → post-process
The cron job prompt instructs the agent to:
1. Generate the full report Markdown (including date filename conventions)
2. Output it as final response
3. A separate post-processing script handles write-to-file + git push

The `script` field in cron job definition runs AFTER the LLM generates output but BEFORE delivery.

---

## Push Script Template

```bash
#!/bin/bash
# push-report.sh — called by Hermes cron job script
# $1 = path to the generated report markdown
# $2 = date string (YYYY-MM-DD)

set -e

REPO_DIR=~/jiujiu-daily
DATE=$2
REPORT_FILE=$1

cd "$REPO_DIR"

# Copy report into reports/
cp "$REPORT_FILE" "reports/$DATE.md"

# Build static site (if build.py exists)
if [ -f build.py ]; then
  python3 build.py
fi

# Git commit and push
git add -A
git commit -m "daily: $DATE 九九晨报"
git push origin main
```

---

## Pitfalls

1. **SSH key must be added to GitHub** — `gh auth login` with token is more reliable for first-time setup
2. **Token expiry** — GitHub PATs expire; set a calendar reminder or use fine-grained tokens with no expiry
3. **git push conflicts** — if two cron runs overlap (unlikely at 24h interval) or manual edits happen, `git pull --rebase` before push
4. **edge-tts dependency** — `pip install edge-tts` required for `build.py` audio generation; if not installed, build will fail silently
5. **GitHub Pages** — the repo is not GitHub Pages enabled by default. Enable in repo settings → Pages → deploy from main branch /docs or root
6. **`gh` CLI first use** requires interactive auth flow — use `--with-token` flag for headless setup
