# wealth-invest-daily Deployment Variant

## Overview

An alternative deployment to `jiujiu-daily`. Different repo name, simpler workflow.

- **Repo**: `corinwe/wealth-invest-daily` (private or public)
- **Purpose**: Pure Markdown archive of daily morning reports — no `build.py`, no TTS, no static site
- **Delivery model**: Cron job `deliver: origin` — agent output IS the report, system auto-delivers to Feishu/WeChat; GitHub commit is a side effect for archiving

## Workflow (Direct Agent Execution — No Script)

When the cron job's `script:` field is missing/broken (e.g., `/root/.hermes/scripts/update_cron_task.sh not found`), the agent handles the entire flow inline:

### Step 1: Data Collection (Parallel)
Use `delegate_task` with 2-3 threads:
- **Thread A**: HK stocks (Alibaba/MI/Meituan) + HK indices
- **Thread B**: US stocks (MSFT/ECL/NVDA) + US market closes + AI sector
- **Thread C**: A-shares (BYD/Midea) + Shanghai/Shenzhen indices

### Step 2: Compile Report
800-character Chinese-lang report with sections:
- Portfolio tracking (per-holding price range + key developments)
- Market overview (all indices in a table)
- AI/Tech sector updates
- Today's focus items

### Step 3: Write + Push (Inline, No Script)

```bash
# Ensure repo exists — clone if missing
if [ ! -d /tmp/wealth-invest-daily/.git ]; then
  git clone https://github.com/corinwe/wealth-invest-daily.git /tmp/wealth-invest-daily
fi

# Create reports dir
mkdir -p /tmp/wealth-invest-daily/reports

# Write the report file
# (use write_file tool → /tmp/wealth-invest-daily/reports/YYYY-MM-DD.md)

# Push to GitHub
cd /tmp/wealth-invest-daily && \
git pull --rebase origin main 2>/dev/null; \
git add reports/YYYY-MM-DD.md && \
git config user.name "Hermes Agent (九九)" && \
git config user.email "corin@offerpath.com" && \
git commit -m "📈 九九财富投资晨报 - YYYY-MM-DD" && \
git push origin main
```

### Step 4: Output Report
The agent's final response IS the morning report text — system auto-delivers to Feishu/WeChat.

## Key Differences from jiujiu-daily

| Aspect | jiujiu-daily | wealth-invest-daily |
|--------|-------------|-------------------|
| Build step | `build.py` (TTS + HTML static site) | None — pure Markdown |
| Delivery | `script:` field writes + pushes | Agent writes + pushes inline |
| Cron `deliver` | `origin` (no auto-delivery) | Auto-delivery to Feishu/WeChat |
| Push method | Shell script | `terminal` tool inline |
| Clone location | `~/jiujiu-daily` | `/tmp/wealth-invest-daily` |

## Pitfalls

1. **Script: field broken ≠ task failure** — If the cron's `script` points to a nonexistent file, the agent still receives the full prompt and can execute the task directly. Do not abort. The cron infrastructure logs the script error but the LLM prompt proceeds normally.
2. **Git user config must be set each time** — The `/tmp` clone won't have persisted git user.name/user.email. Always set them before committing.
3. **Avoid bad state** — If the repo is already dirty (from a prior failed run), the git pull --rebase may conflict. Check with `git status` before add/push if errors occur.
4. **write_file path must match what git add targets** — Use full absolute path `/tmp/wealth-invest-daily/reports/YYYY-MM-DD.md`.
5. **No user present** — The cron job runs headless. No questions, no clarifications. Make reasonable decisions about data accuracy, format, and content.
