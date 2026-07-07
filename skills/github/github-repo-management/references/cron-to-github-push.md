# Cron-to-GitHub Push Workflow

When a cron-generated script or report needs to be automatically committed and pushed to a GitHub repo (e.g. daily reports, generated site builds), use this pattern.

## Architecture

```
Cron task (Hermes Agent)
  → generates stdout / markdown output
  → post-processing script writes to working-copy/reports/YYYY-MM-DD.md
  → runs build.py (if the repo has one for HTML/etc. generation)
  → git add + commit + push to remote
```

## Setup Checklist

### 1. Clone the repo as a local working copy

```bash
mkdir -p ~/.hermes/repos/
git clone git@github.com:owner/repo.git ~/.hermes/repos/repo-name
```

### 2. Create a push script (`~/.hermes/scripts/push-to-github.sh`)

```bash
#!/usr/bin/env bash
# Called by the cron job after writing the report file.
# Args: $1 = repo_path, $2 = commit_message
set -euo pipefail

REPO_PATH="$1"
COMMIT_MSG="${2:-Auto-update}"

cd "$REPO_PATH"

# Ensure we're on the right branch
git checkout main 2>/dev/null || git checkout master 2>/dev/null

# Stash any pending changes before pulling
git stash push -m "auto-stash-before-pull" 2>/dev/null || true

# Pull latest to avoid push conflicts
git pull --rebase origin main 2>/dev/null || git pull --rebase origin master 2>/dev/null

# Restore stashed changes
git stash pop 2>/dev/null || true

# Add new/changed files
git add -A

# Only commit if there are changes
if git diff --cached --quiet; then
    echo "No changes to commit."
    exit 0
fi

git commit -m "$COMMIT_MSG"

# Push via HTTPS (credential helper) or SSH
git push origin main 2>/dev/null || git push origin master 2>/dev/null
```

### 3. Wire into the cron job

In the cron job's answer/prompt, tell the agent to **write the report output** to a file in the working copy, then call the push script. Example instruction at the bottom of the cron prompt:

```
When you finish your report output, run:
  cat << 'REPORT_EOF' > ~/.hermes/repos/repo-name/reports/YYYY-MM-DD.md
  [your report content here]
  REPORT_EOF

Then run:
  cd ~/.hermes/repos/repo-name && python3 build.py
  bash ~/.hermes/scripts/push-to-github.sh ~/.hermes/repos/repo-name "晨报 YYYY-MM-DD"
```

For an even cleaner approach, configure the cron job with `deliver: script` (Hermes Agent v0.13+ cron scripting) so the LLM output is piped directly through a post-processing script instead of the agent having to self-execute.

## Common Pitfalls

- **SSH key not added to GitHub** — `ssh -T git@github.com` will return `Permission denied`. Fix: add public key to GitHub Settings → SSH and GPG keys.
- **No git user configured** — commits fail with `Please tell me who you are`. Fix: `git config --global user.name "..."` and `git config --global user.email "..."`
- **Push rejected (non-fast-forward)** — the remote has commits the local doesn't. Fix: `git pull --rebase origin main` before committing.
- **Credential helper not set** — HTTPS pushes prompt for password. Fix: `git config --global credential.helper store` and authenticate once.
- **Large report directory** — over time `git log` can slow down. Not a problem for text-only markdown files; consider `.gitignore` for generated binary assets if applicable.

## Validated Pattern: Direct Cron + SSH Push (方案A)

For Hermes Agent v0.13+ cron tasks that generate daily reports, the following pattern is validated to work. Called **方案A** because the LLM agent itself writes files and runs git commands (vs. delegating to a bash script).

### 1. Clone the repo to a stable path

```bash
git clone git@github.com:owner/repo-name.git /tmp/repo-name
```

The `/tmp/` path is fine — the cron job runs on the same machine and the clone persists across cron executions. Pull to stay in sync with remote changes.

### 2. Configure the cron task prompt

In the cron prompt, instruct the agent to **write the report to the repo directory** and **run git commands** as part of its execution (after generating the report/code). Structure the prompt like this:

```
## 💾 保存到文件 + 推送 GitHub
生成完内容后，按以下步骤操作：

**步骤1：** 用 write_file 工具将内容保存到 /tmp/repo-name/reports/$(date +%Y-%m-%d).md

**步骤2：** 用 terminal 执行 build（如果有 build.py）：
```
cd /tmp/repo-name && python3 build.py
```

**步骤3：** 用 terminal 执行推送：
```
cd /tmp/repo-name && \
git add reports/$(date +%Y-%m-%d).md && \
git diff --cached --quiet || ( \
  git config user.name "Bot Name" && \
  git config user.email "bot@example.com" && \
  git commit -m "📈 Daily Report - $(date +%Y-%m-%d)" && \
  git push origin main \
)
```
```

Key design choices:
- **`git diff --cached --quiet || (...)`** — only commits if there are actual changes, avoiding empty commits
- **`git add` before checking diff** — stage the new file first, then check if anything changed
- **`--rebase` pull omitted** — on a single-actor repo (only the cron pushes), pulls are unnecessary and add failure modes. Add back `git pull --rebase origin main 2>/dev/null;` before add+commit if multiple actors push to the repo.

### 3. Use `deliver: all` for multi-platform delivery

When you also want the report delivered via other platforms (Feishu, WeChat), set the cron task's `deliver` field to `all` so the system automatically sends the LLM's final response to all connected platforms in addition to the GitHub push.

```bash
hermes cron update <job-id> --deliver all
```

Make sure the cron job's `script` field is cleared (empty string, not omitted) to avoid the agent trying to run a non-existent script:

```bash
hermes cron update <job-id> --script ""
```

### 4. GitHub Pages Deployment (Browsable Reports)

To make cron-generated reports viewable as a website (GitHub Pages), add these files to the repo:

#### File: `build.py`

A Python script that reads all Markdown files from `reports/`, extracts metadata (date, word count, sections, summary), and injects them into HTML templates.

```python
#!/usr/bin/env python3
import os, re, json, glob

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(SITE_DIR, 'reports')
INDEX_TPL = os.path.join(SITE_DIR, 'index.template.html')
INDEX_OUT = os.path.join(SITE_DIR, 'index.html')
REPORT_TPL = os.path.join(SITE_DIR, 'report.template.html')
REPORT_OUT = os.path.join(SITE_DIR, 'report.html')
PLACEHOLDER = 'REPORTS_JSON_PLACEHOLDER'

def extract_metadata(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    meta = {'date': '', 'file': os.path.basename(filepath), 'summary': '', 'sections': [], 'word_count': 0}
    date_match = re.match(r'(\d{4}-\d{2}-\d{2})', meta['file'])
    if date_match:
        meta['date'] = date_match.group(1)
    text_only = re.sub(r'[#*`\[\]|>]', '', content)
    meta['word_count'] = len(re.findall(r'[\u4e00-\u9fff]', text_only)) + len(re.findall(r'[a-zA-Z]+', text_only))
    for m in re.finditer(r'^## ([^\n]+)', content, re.MULTILINE):
        meta['sections'].append({'title': re.sub(r'\*\*', '', m.group(1).strip()), 'anchor': ''})
    conclusion = re.search(r'>\s*(.+?)(?:\n\n|\Z)', content, re.DOTALL)
    if conclusion:
        meta['summary'] = re.sub(r'\s+', ' ', conclusion.group(1).strip())[:200]
    if not meta['summary']:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('##') and i > 0:
                paras = [l.strip() for l in range(i-2,i) if lines[l].strip() and not lines[l].startswith('#') and not lines[l].startswith('---')]
                if paras:
                    meta['summary'] = ' '.join(paras)[:200]
                break
    return meta

def scan_reports():
    return sorted([m for f in sorted(glob.glob(os.path.join(REPORTS_DIR, '*.md')), reverse=True) if (m := extract_metadata(f)) and m['date']], key=lambda x: x['date'], reverse=True)

def build(tpl_path, out_path, reports_json):
    with open(tpl_path, 'r', encoding='utf-8') as f:
        html = f.read().replace(PLACEHOLDER, reports_json)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    reports_json = json.dumps(scan_reports(), ensure_ascii=False, indent=2)
    for tpl, out in [(INDEX_TPL, INDEX_OUT), (REPORT_TPL, REPORT_OUT)]:
        build(tpl, out, reports_json)
```

#### File: `index.template.html`

The main listing page. Must contain the exact placeholder string `REPORTS_JSON_PLACEHOLDER` where the JS variable `const REPORTS = ...` should go. The placeholder gets replaced at build time with the full JSON metadata array.

Template structure:
- Dark theme with gold accent colors
- Header with update badge and stats (report count, total words, sections)
- Search bar for filtering by date or keyword
- Month-grouped report cards showing date, weekday, word count, sections, and summary
- Latest report gets a `LATEST` tag and highlighted border

#### File: `report.template.html`

The detail page for individual reports. Also contains `REPORTS_JSON_PLACEHOLDER`. Features:
- Navigation: "← 所有晨报" back button, "← 上期 / 下期 →" for sequential browsing
- Fetches the raw Markdown file from `reports/` via `fetch()`, renders it through `marked.parse()`, sanitizes with `DOMPurify`
- Renders markdown tables, blockquotes, lists in the dark theme

#### Workflow

After each cron push:
1. Agent writes report to `/tmp/repo-name/reports/YYYY-MM-DD.md`
2. Agent runs `cd /tmp/repo-name && python3 build.py` to regenerate HTML
3. Agent runs `git add` + `commit` + `push` (including the new/updated HTML files)

#### GitHub Pages Configuration

The user must enable Pages in the repo settings:
- Settings → Pages → Source: "Deploy from a branch"
- Branch: `main`, directory: `/ (root)`
- The site will be available at `https://<user>.github.io/<repo-name>/`

### 5. On first setup, verify push works manually

```bash
# Create a test report file
echo "# Test Report" > /tmp/repo-name/reports/$(date +%Y-%m-%d).md
cd /tmp/repo-name
git add reports/$(date +%Y-%m-%d).md
git commit -m "📈 Test - $(date +%Y-%m-%d)"
git push origin main
```

### 6. SSH Key Mismatch Recovery

If `ssh -T git@github.com` returns `Permission denied` even after adding the key:

1. **Check for mismatch**: If the error says `identity_sign: private key /... contents do not match public`, the local key pair is broken. The agent must generate a **new** key pair on the server.
2. **Regenerate**: `ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -C "email@example.com"`
3. **Get the new public key**: `cat ~/.ssh/id_ed25519.pub`
4. **Ask the user to**:
   - Go to GitHub Settings → SSH and GPG keys
   - **Remove** the old (mismatched) key first — GitHub won't allow two keys with the same title
   - **Add** the new public key with a recognizable title (e.g., "bot-name-server")
5. **Verify**: `ssh -T git@github.com` should now show `Hi <user>! You've successfully authenticated...`

> **Key insight**: The agent generates the key, the user adds it to GitHub. The agent must output the full public key text for the user to copy-paste.

### 7. Common Pitfalls Summary

| Pitfall | Cause | Fix |
|---------|-------|-----|
| `Script not found` error in cron | `script` field points to a non-existent file | `hermes cron update <id> --script ""` |
| Empty commits | `git commit` runs even with no changes | Wrap in `git diff --cached --quiet || (...)` |
| Push rejected | Remote has commits local doesn't | `git pull --rebase origin main` before commit |
| SSH key mismatch | private/public key pair corrupted | Generate new pair, user removes old key + adds new one |
| Pages not updating | Only markdown pushed, HTML stale | Run `build.py` before `git add` to regenerate HTML |
