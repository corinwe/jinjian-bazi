#!/bin/bash
# Create deployment packages for miniprogram
# Usage: ./create_deployment_package.sh

set -e

BASE_DIR="/root/.openclaw/workspace/offerpath"
MINIPROGRAM_DIR="$BASE_DIR/miniprogram"
API_SERVER_FILE="$BASE_DIR/api-server.js"
START_SCRIPT="$BASE_DIR/start-api.sh"
VERSION="v2.1.97"
DATE=$(date +%Y%m%d)

# Create miniprogram-only package
echo "Creating miniprogram package..."
tar -czf "$BASE_DIR/offerpath-miniprogram-$VERSION-$DATE.tar.gz" -C "$BASE_DIR" miniprogram/

# Create full package with API server
echo "Creating full package..."
tar -czf "$BASE_DIR/offerpath-full-$VERSION-$DATE.tar.gz" -C "$BASE_DIR" miniprogram/ api-server.js start-api.sh

# List created packages
echo "\nCreated packages:"
ls -lh "$BASE_DIR/offerpath-*$DATE.tar.gz"

echo "\nPackages created successfully!"