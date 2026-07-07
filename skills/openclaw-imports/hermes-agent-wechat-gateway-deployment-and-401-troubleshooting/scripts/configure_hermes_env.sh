#!/bin/bash
# Configure Hermes Agent environment variables for DeepSeek V4 and WeChat gateway
# Usage: ./configure_hermes_env.sh [deepseek_api_key]

set -e

ENV_FILE="/root/.hermes/.env"
DEEPSEEK_API_KEY="${1:-sk-bec7b80231fa42ddb2af2c73634ce8ac}"

# Ensure .hermes directory exists
mkdir -p /root/.hermes

# Backup existing .env if present
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "${ENV_FILE}.bak.$(date +%Y%m%d%H%M%S)"
    echo "Backed up existing .env"
fi

# Write configuration
cat > "$ENV_FILE" << EOF
# DeepSeek API
DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}

# WeChat Gateway (will be updated after weixin_accounts.json is created)
# WEIXIN_ACCOUNT_ID=<from weixin_accounts.json>
# WEIXIN_TOKEN=<from weixin_accounts.json>
WEIXIN_BASE_URL=https://ilinkai.weixin.qq.com/ilink/bot
GATEWAY_ALLOW_ALL_USERS=true
EOF

echo "✅ Environment file created at $ENV_FILE"
echo "⚠️  You still need to:"
echo "  1. Run 'hermes gateway setup' to scan QR code and login"
echo "  2. Extract WEIXIN_ACCOUNT_ID and WEIXIN_TOKEN from /root/.hermes/weixin_accounts.json"
echo "  3. Add them to $ENV_FILE"