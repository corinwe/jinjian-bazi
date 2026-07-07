#!/bin/bash
# Fix bash wrapper infinite recursion for hermes command
# Removes the broken bash wrapper and creates a symlink to the venv binary

set -e

HERMES_VENV_BIN="/usr/local/lib/hermes-agent/venv/bin/hermes"
HERMES_SYMLINK="/usr/local/bin/hermes"

if [ -f "$HERMES_VENV_BIN" ]; then
    echo "Found hermes binary at $HERMES_VENV_BIN"
    # Remove existing broken wrapper or symlink
    if [ -f "$HERMES_SYMLINK" ] || [ -L "$HERMES_SYMLINK" ]; then
        rm -f "$HERMES_SYMLINK"
        echo "Removed existing $HERMES_SYMLINK"
    fi
    # Create correct symlink
    ln -sf "$HERMES_VENV_BIN" "$HERMES_SYMLINK"
    echo "Created symlink: $HERMES_SYMLINK -> $HERMES_VENV_BIN"
    # Verify
    if command -v hermes &> /dev/null; then
        echo "✅ hermes command is now working correctly"
        hermes --version 2>/dev/null || echo "(version check may fail if not fully configured)"
    fi
else
    echo "❌ hermes binary not found at $HERMES_VENV_BIN"
    echo "Please install Hermes Agent first: curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash"
    exit 1
fi