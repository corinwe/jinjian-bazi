# Session Reset Strategies — Context Continuity Without Disabling Reset

## The Problem

Hermes Agent resets session context on a schedule (`session_reset.at_hour: 4`, default 4 AM). This clears conversation history but **preserves persistent memory** (the `memory` tool) and **session files on disk** (accessible via `session_search`).

When the user expects continuity across days ("重置了就丢失记忆了可不行啊！！"), raw session_search on every turn is too slow and unreliable. This document catalogs strategies for maintaining context continuity without disabling the reset.

## Strategy 1: Cron + Memory Auto-Archive (Recommended)

Set a cron job shortly after the daily reset hour (e.g., 4:10 AM) to:
1. Run `session_search` to retrieve the previous day's key conversation
2. Extract: user instructions, decisions made, documents received, corrections, pending tasks
3. Write the summary into persistent memory via the `memory` tool
4. Optionally write to a file for additional reference

**Trade-offs:**
- ✅ Zero config changes to Hermes Agent
- ✅ Works with existing session_reset config (mode: both, at_hour: 4)
- ✅ Memory survives reset, so the next session loads it automatically
- ❌ Cron job runs even if no conversation happened (wastes a turn)
- ❌ Summary quality depends on session_search recall quality

**Implementation sketch:**
```yaml
cron:
  schedule: "10 4 * * *"   # 4:10 AM daily
  prompt: |
    Search recent sessions for key content from yesterday.
    Extract: user requests, documents received, corrections, pending tasks.
    Save a concise summary to memory (~800 chars max).
    Also write to file /root/.hermes/profiles/jinjian-zhenren/cache/daily_summary_latest.md
```

## Strategy 2: Active Save During Session

During important interactions, proactively write critical context to memory **immediately** (not waiting for the cron). This handles the case where the session ends before the cron runs.

**When to trigger:**
- User sends documents (save names, status, key findings)
- User gives a correction (save the correction verbatim)
- User assigns a multi-turn task (save progress checkpoint)
- User expresses a preference (save to both memory and skill)

**Memory budget:** 2200 chars total. Use it for the most recent / most urgent context. Old entries get overwritten by new ones. The cron summary provides full-day coverage.

## Strategy 3: Cron + File Restore (Hermes CLI — `--continue`)

For CLI sessions, the user can resume the most recent session:
```bash
hermes --continue
```
This restores the exact conversation context from the last session. Not applicable to Feishu gateway sessions.

## Strategy 4: Disable Daily Reset Altogether

```yaml
session_reset:
  mode: none   # never auto-reset
```

**Trade-offs:**
- ✅ Perfect continuity — never lose context
- ❌ Context grows indefinitely → slower responses, higher API costs
- ❌ After weeks of daily use, context far exceeds model's effective window
- ❌ Model suffers "lost in the middle" — early instructions get ignored

Not recommended unless the user explicitly accepts the costs.

## Strategy 5: Push Daily Reset to Off-Hours

```yaml
session_reset:
  mode: daily          # only daily reset, no idle timeout
  at_hour: 2           # 2 AM — user almost certainly asleep
```

This gives the user a full day of uninterrupted conversation. The reset only happens once at 2 AM. If the user is chatting at 2 AM, the reset fires after that conversation ends.

**Best for:** Users who chat heavily during the day and don't want mid-conversation resets.

## Which Strategy for Which User

| User pattern | Recommended strategy |
|-------------|---------------------|
| Heavy daily use, many documents | Strategy 1 (cron archive) + Strategy 2 (active save) |
| Occasional use, short sessions | Strategy 1 alone |
| Late-night user, long sessions | Strategy 5 (push to 2 AM) |
| CLI-only user | Strategy 3 (--continue) |
| Accepts cost/speed trade-off | Strategy 4 (mode: none) |

## Key Principles

1. **Memory is the backbone** — Hermes' persistent memory tool survives every reset. Always prefer writing to memory over writing to files when possible.
2. **session_search is the safety net** — it can retrieve any past conversation. Use it for recovery, not for routine context loading.
3. **Prioritize the user's last instruction** — the most recent session matters most. If memory is full, overwrite the oldest entry, not the newest.
4. **Skill updates are permanent** — when the user gives a preference/correction, put it in the relevant skill's SKILL.md, not just memory. Skills survive curator pruning; old memory entries age out.
