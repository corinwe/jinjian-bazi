#!/bin/bash
# Start Hermes WeChat gateway directly via Python module
# Bypasses the bash wrapper to avoid infinite recursion

set -e

HERMES_VENV_PYTHON="/usr/local/lib/hermes-agent/venv/bin/python"

if [ ! -f "$HERMES_VENV_PYTHON" ]; then
    echo "❌ Hermes venv Python not found at $HERMES_VENV_PYTHON"
    echo "Please install Hermes Agent first: curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash"
    exit 1
fi

# Check for required environment variables
if [ -z "$WEIXIN_ACCOUNT_ID" ] || [ -z "$WEIXIN_TOKEN" ]; then
    echo "⚠️  WEIXIN_ACCOUNT_ID or WEIXIN_TOKEN not set in environment"
    echo "Checking /root/.hermes/.env..."
    if [ -f /root/.hermes/.env ]; then
        source /root/.hermes/.env
        if [ -z "$WEIXIN_ACCOUNT_ID" ] || [ -z "$WEIXIN_TOKEN" ]; then
            echo "❌ Please configure WEIXIN_ACCOUNT_ID and WEIXIN_TOKEN in /root/.hermes/.env"
            echo "   (Run 'hermes gateway setup' first to generate weixin_accounts.json)"
            exit 1
        fi
    else
        echo "❌ /root/.hermes/.env not found. Run configure_hermes_env.sh first."
        exit 1
    fi
fi

echo "🚀 Starting Hermes WeChat gateway..."
echo "   Account ID: $WEIXIN_ACCOUNT_ID"
echo "   Base URL: ${WEIXIN_BASE_URL:-https://ilinkai.weixin.qq.com/ilink/bot}"
echo "   Allow all users: ${GATEWAY_ALLOW_ALL_USERS:-true}"
echo ""
echo "Press Ctrl+C to stop"

# Start gateway directly via Python module
exec "$HERMES_VENV_PYTHON" -m hermes.gateway.run