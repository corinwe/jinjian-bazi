# Syncing DeepSeek Provider Config to Co-located OpenClaw

When Hermes Agent and OpenClaw run on the same server and need matching DeepSeek model/provider settings.

## OpenClaw Config Location

```
/root/.openclaw/openclaw.json
```

Key sections:

```json
{
  "models": {
    "providers": {
      "deepseek": {
        "baseUrl": "https://api.deepseek.com",
        "apiKey": "<key>",
        "api": "openai-completions",
        "models": [
          { "id": "deepseek-v4-flash", "name": "DeepSeek-V4-flash", ... },
          { "id": "deepseek-chat", "name": "DeepSeek-Chat", ... }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "deepseek/deepseek-chat"
      }
    }
  }
}
```

## Procedure

### 1. Copy API key from Hermes without exposing it

The config file display is automatically masked by read_file and terminal output. Use a Python heredoc to copy the key directly:

```python
python3 << 'PYEOF'
import json, re

# Read Hermes config
with open('/root/.hermes/config.yaml', 'rb') as f:
    hermes_cfg = f.read()

# Extract the main model's api_key (first match)
matches = list(re.finditer(rb'api_key:\s+(\S+)', hermes_cfg))
hermes_key = matches[0].group(1).decode()

# Read OpenClaw config
with open('/root/.openclaw/openclaw.json', 'r') as f:
    oc = json.load(f)

# Update key
oc['models']['providers']['deepseek']['apiKey'] = hermes_key

# Write back
with open('/root/.openclaw/openclaw.json', 'w') as f:
    json.dump(oc, f, indent=2)
PYEOF
```

### 2. Add missing models

OpenClaw's deepseek provider may only have `deepseek-v4-flash`. If the default agent model references `deepseek/deepseek-chat`, add it:

```python
if 'deepseek-chat' not in [m['id'] for m in oc['models']['providers']['deepseek']['models']]:
    oc['models']['providers']['deepseek']['models'].append({
        "id": "deepseek-chat",
        "name": "DeepSeek-Chat",
        "reasoning": False,
        "input": ["text"],
        "contextWindow": 128000,
        "maxTokens": 8192,
        "cost": {"input": 0.28, "output": 0.42, "cacheRead": 0.028, "cacheWrite": 0.28}
    })
```

### 3. Set default agent model

```python
oc['agents']['defaults']['model']['primary'] = 'deepseek/deepseek-chat'
```

### 4. Start / restart OpenClaw

```bash
openclaw gateway --force
```

If no OpenClaw process is running, `--force` creates one on the default port.

## Verification

After updating, verify with:

```bash
python3 -c "
import json
with open('/root/.openclaw/openclaw.json') as f:
    oc = json.load(f)
ds = oc['models']['providers']['deepseek']
print(f'Key: {len(ds[\"apiKey\"])} chars')
print(f'Models: {[m[\"id\"] for m in ds[\"models\"]]}')
print(f'Default: {oc[\"agents\"][\"defaults\"][\"model\"][\"primary\"]}')
"
```

## Pitfalls

- **API key length mismatch**: Hermes keys are 35 chars (`sk-` + 32 hex), OpenClaw may have had a different-length key. After syncing, verify the key length matches what Hermes uses.
- **read_file masking**: The `read_file` tool masks API keys with `...` in the displayed output. The actual file content is unmasked. Always use programmatic copy (heredoc) rather than manual re-typing.
- **OpenClaw not running as a service**: On this server, OpenClaw has no systemd service or PM2 daemon. It must be started manually with `openclaw gateway --force`. There is no auto-start on boot.
- **OpenClaw gateway port**: Default is 32544 (same as Hermes gateway if configured). Use `openclaw gateway --port <N>` if ports conflict.
- **Gateway daemon lifecycle**: `openclaw gateway --force` spawns a background daemon process (`openclaw-gateway`) that persists after the CLI command exits. The CLI parent process typically exits with code 1 even on success — this is normal. Verify the daemon is running with `ss -tlnp | grep 32544` or `ps aux | grep openclaw-gateway`. The daemon uses ~793MB of resident memory and ~22GB virtual.
- **Health endpoint may not respond**: The gateway's `/health` endpoint on port 32544 may hang or timeout. Use the port listener check instead as a reliable alive test.
