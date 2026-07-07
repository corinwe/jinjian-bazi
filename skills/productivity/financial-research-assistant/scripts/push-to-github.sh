#!/bin/bash
# push-to-github.sh — Push morning report to GitHub repo
# Usage: push-to-github.sh <report_markdown_path> <date_yyyy-mm-dd>
#
# Called by Hermes cron job script. Handles:
# 1. Copy report into reports/
# 2. Run build.py (TTS + static site)
# 3. Git commit + push

set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/jiujiu-daily}"
REPORT_FILE="$1"
DATE="$2"

if [ ! -f "$REPORT_FILE" ]; then
  echo "ERROR: Report file not found: $REPORT_FILE" >&2
  exit 1
fi

cd "$REPO_DIR"

# Pull latest to avoid conflicts
git pull --rebase origin main 2>/dev/null || true

# Copy report
mkdir -p reports
cp "$REPORT_FILE" "reports/$DATE.md"
echo "✅ Copied report to reports/$DATE.md"

# Build static site
if [ -f build.py ]; then
  if command -v python3 &>/dev/null; then
    python3 build.py
    echo "✅ Static site built"
  else
    echo "⚠️ python3 not available, skipping build"
  fi
fi

# Commit and push
git add -A
git commit -m "daily: $DATE 九九晨报"
git push origin main
echo "✅ Pushed to GitHub: corinwe/jiujiu-daily"
