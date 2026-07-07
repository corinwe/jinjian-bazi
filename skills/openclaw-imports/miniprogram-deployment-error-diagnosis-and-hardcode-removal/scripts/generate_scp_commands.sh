#!/bin/bash
# Generate SCP commands for copying deployment packages
# Usage: ./generate_scp_commands.sh

set -e

SERVER_IP="43.162.90.39"
BASE_DIR="/root/.openclaw/workspace/offerpath"

# Find the latest packages
LATEST_FULL=$(ls -t "$BASE_DIR/offerpath-full-"*.tar.gz | head -1)
LATEST_MINI=$(ls -t "$BASE_DIR/offerpath-miniprogram-"*.tar.gz | head -1)

# Extract filenames
FULL_PKG=$(basename "$LATEST_FULL")
MINI_PKG=$(basename "$LATEST_MINI")

# Generate SCP commands
echo "# SCP Commands for Server: $SERVER_IP"
echo ""
echo "# 1. Copy full package (recommended):"
echo "scp root@$SERVER_IP:$LATEST_FULL ."
echo ""
echo "# 2. Copy miniprogram only:"
echo "scp root@$SERVER_IP:$LATEST_MINI ."
echo ""
echo "# 3. Copy all related files:"
echo "scp root@$SERVER_IP:$BASE_DIR/offerpath-*.tar.gz ."
echo "scp root@$SERVER_IP:$BASE_DIR/DEPLOYMENT-README.md ."
echo "scp root@$SERVER_IP:$BASE_DIR/SCP-COMMANDS.md ."
echo ""
echo "# 4. Test connection:"
echo "ssh root@$SERVER_IP \"echo 'Connection successful'\""
echo ""
echo "# 5. Verify files exist:"
echo "ssh root@$SERVER_IP \"ls -lh $BASE_DIR/offerpath-*.tar.gz\""