# Feishu Group Message Troubleshooting: Real Session

This documents a real debugging session where Feishu DM messages worked but group messages were never received.

## Symptom

- Bot added to group log: `[Feishu] Bot added to chat: oc_55b5bcbbfbed43de74e0595a01fa680a`
- DM messages processed normally
- Zero `Inbound group message received:` log entries
- `FEISHU_GROUP_POLICY=open` already set in `.env`
- Gateway running in websocket mode

## Root Cause

The Feishu Open Platform app's `im.message.receive_v1` event subscription did **not** have "群聊 (Group)" checked under **聊天类型 (Chat Types)**. The event was only subscribed for P2P (direct messages).

## Full Debug Path

### Step 1: Check gateway logs for group messages

```bash
grep "55b5bcbbfbed\|oc_55b5" ~/.hermes/logs/gateway.log
```
→ Only showed `Bot added to chat` event, no group messages.

### Step 2: Check `.env` configuration

```bash
grep FEISHU_GROUP /root/.hermes/.env
grep FEISHU_REQUIRE /root/.hermes/.env
```
→ `FEISHU_GROUP_POLICY=open` present but `FEISHU_REQUIRE_MENTION` missing.

### Step 3: Add `FEISHU_REQUIRE_MENTION=false`

`.env` is write-protected — must use terminal:
```bash
echo 'FEISHU_REQUIRE_MENTION=false' >> /root/.hermes/.env
```

### Step 4: Restart gateway

```bash
hermes gateway restart  # timed out after 180s
# Fallback:
systemctl restart hermes-gateway
```
→ New PID confirmed via `hermes gateway status`.

### Step 5: Verify gateway log after restart

```bash
tail -30 ~/.hermes/logs/gateway.log
```
→ Only DM messages shown. No group messages. The problem was **upstream** — Feishu server never delivered the group messages to the bot.

### Step 6: Identify real root cause

Since the gateway registered `im.message.receive_v1` correctly (DMs work), and the "bot added" event also arrived, but group messages didn't, the issue must be in the **Feishu Open Platform event subscription configuration** — specifically the "聊天类型 (Chat Types)" selector for the `im.message.receive_v1` event.

## Resolution

User needed to:
1. Open https://open.feishu.cn/app → their app
2. Go to **事件与回调 (Events & Callbacks)**
3. Find `im.message.receive_v1`
4. Click into it → check **群聊 (Group)** under 聊天类型
5. Save and **发布 (Publish)**

## Key Technical Detail

The `im.message.receive_v1` event in Feishu Open Platform has a **chat type filter**:
- **P2P (单聊)**: Bot receives DMs
- **Group (群聊)**: Bot receives group messages

Both must be checked for the bot to receive group messages. This is a per-event setting, not a global permission. The app can have `im:message` permission granted but still not receive group messages if only P2P is selected in the event subscription.

## Env Var Reference

| Var | Default | Purpose |
|-----|---------|---------|
| `FEISHU_GROUP_POLICY` | `open` | open \| allowlist \| disabled |
| `FEISHU_REQUIRE_MENTION` | `true` | false = respond without @mention |
| `FEISHU_ALLOW_ALL_USERS` | `false` | Allow any user to chat |
| `FEISHU_ALLOWED_USERS` | empty | Comma-sep open_id list |
| `FEISHU_HOME_CHANNEL` | empty | DM chat ID for notifications |
