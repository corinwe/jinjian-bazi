# Provider Fallback Configuration (OpenRouter)

## Problem
When the primary LLM provider (e.g., DeepSeek API) goes down or returns errors, the agent needs a fallback. Without one, cron jobs fail silently or sessions hang.

## Solution: OpenRouter as Fallback

### 1. Add API key to `.env`
```bash
echo "OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" >> ~/.hermes/.env
```

### 2. Configure in config.yaml
```bash
hermes config set providers.openrouter.api_key 'sk-or-...'
hermes config set providers.openrouter.model 'deepseek/deepseek-chat'
hermes config set fallback_providers '["openrouter"]'
```

### 3. Verify connection
```bash
curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek/deepseek-chat",
    "messages": [{"role": "user", "content": "OK"}],
    "max_tokens": 10
  }'
```

## Provider TOS Notes
- **Anthropic models** (claude-sonnet-4, claude-opus-4) via OpenRouter may return 403: "violation of provider Terms Of Service" if the API key origin or IP isn't whitelisted
- **DeepSeek models** via OpenRouter work reliably (tested May 2026, routes through Novita)
- **Google models** (gemini-*) via OpenRouter require separate whitelist

## Recommended Setup
```
Primary:    deepseek-chat (direct via custom provider, api.deepseek.com)
Fallback:   deepseek/deepseek-chat (via OpenRouter, same model different path)
```

This ensures the same model behavior with independent provider infrastructure.

## Memory Note
Store only "已配置OPENROUTER_API_KEY" in memory, not the key itself. The key lives in `.env` only.
