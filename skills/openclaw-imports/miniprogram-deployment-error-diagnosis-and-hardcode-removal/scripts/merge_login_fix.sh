#!/bin/bash
# Merge login bug fix from one miniprogram version to another
# Usage: ./merge_login_fix.sh SOURCE_DIR TARGET_DIR

set -e

if [ $# -lt 2 ]; then
    echo "Usage: $0 SOURCE_DIR TARGET_DIR"
    echo "Example: $0 /root/.openclaw/workspace/miniprogram /root/.openclaw/workspace/offerpath/miniprogram"
    exit 1
fi

SOURCE_DIR="$1"
TARGET_DIR="$2"
LOGIN_FILE="pages/mine/mine.js"

echo "Merging login bug fix..."
echo "Source: $SOURCE_DIR/$LOGIN_FILE"
echo "Target: $TARGET_DIR/$LOGIN_FILE"

# Check if source file exists
if [ ! -f "$SOURCE_DIR/$LOGIN_FILE" ]; then
    echo "❌ Source file not found: $SOURCE_DIR/$LOGIN_FILE"
    exit 1
fi

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ Target directory not found: $TARGET_DIR"
    exit 1
fi

# Create target directory structure if needed
TARGET_FILE_DIR="$(dirname "$TARGET_DIR/$LOGIN_FILE")"
mkdir -p "$TARGET_FILE_DIR"

# Backup original file if it exists
if [ -f "$TARGET_DIR/$LOGIN_FILE" ]; then
    BACKUP_FILE="$TARGET_DIR/$LOGIN_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$TARGET_DIR/$LOGIN_FILE" "$BACKUP_FILE"
    echo "📦 Created backup: $BACKUP_FILE"
fi

# Copy the fixed file
cp "$SOURCE_DIR/$LOGIN_FILE" "$TARGET_DIR/$LOGIN_FILE"

# Verify the copy
if cmp -s "$SOURCE_DIR/$LOGIN_FILE" "$TARGET_DIR/$LOGIN_FILE"; then
    echo "✅ Login bug fix merged successfully"
    echo "   File size: $(wc -l < "$TARGET_DIR/$LOGIN_FILE") lines"
    echo "   Last modified: $(stat -c %y "$TARGET_DIR/$LOGIN_FILE")"
else
    echo "❌ Files differ after copy"
    exit 1
fi

# Show a sample of the fixed code
echo "\n🔧 Sample of fixed code:"
grep -A 5 -B 5 "userInfo" "$TARGET_DIR/$LOGIN_FILE" | head -20 || true