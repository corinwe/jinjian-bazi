# Hermes Hook 实战架构（2026-07-16 落地记录）

> **来源**：金鉴真人企业级工程架构落地实战
> **关联技能**：hermes-sop-enforcement（核心理论）+ hermes-context-loading（加载链规则）

## 实际配置文件

### config.yaml hooks 块

```yaml
hooks:
  post_tool_call:
    - /root/.hermes/hooks/bazi-mandatory/check.sh
  pre_tool_call:
    - /root/.hermes/hooks/bazi-mandatory/precheck.sh
  pre_llm_call:
    - /root/.hermes/hooks/bazi-mandatory/inject-context.sh
hooks_auto_accept: true
```

### pre_tool_call 物理拦截脚本（Python）

保存到 `/root/.hermes/hooks/bazi-mandatory/precheck.py`：

```python
#!/usr/bin/env python3
"""
pre_tool_call hook — 物理拦截层
在 write_file/patch 执行前，检查是否已通过验证。
未通过验证 → block 交付。
"""
import sys, json, os

def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return

    tool_name = payload.get("tool_name", "")
    args = payload.get("args", {})

    # 只拦截写文件类操作
    if tool_name not in ("write_file", "patch"):
        return

    filepath = args.get("path", "")

    # 只拦截报告文件（.md 且含 报告/分析 关键字）
    if not filepath.endswith(".md"):
        return
    if not any(kw in filepath for kw in ["报告", "分析", "report", "analysis"]):
        return

    # 检查是否已经过了 pillar-verify
    verify_flag = "/tmp/.bazi_verified"
    if os.path.exists(verify_flag):
        os.remove(verify_flag)
        return

    # 没验证 → block
    result = {
        "action": "block",
        "message": (
            f"⛔ 物理拦截：写入 {filepath} 前未通过 pillar-verify。\n"
            f"请先执行：bash projects/bazi-platform/scripts/pillar-verify.py\n"
            f"验证通过后再写文件。"
        )
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
```

### Shell hook wrapper（适配 Shell hooks 协议）

保存到 `/root/.hermes/hooks/bazi-mandatory/precheck.sh`：

```bash
#!/usr/bin/env python3
"""
pre_tool_call shell hook wrapper
Shell hooks 接收 stdin JSON，输出 stdout JSON。
"""
import sys, json, subprocess

result = subprocess.run(
    [sys.executable, "/root/.hermes/hooks/bazi-mandatory/precheck.py"],
    input=sys.stdin.read(),
    capture_output=True,
    text=True,
    timeout=15
)
if result.stdout.strip():
    print(result.stdout.strip())
```

### pre_llm_call 提醒脚本（每次回答前注入）

保存到 `/root/.hermes/hooks/bazi-mandatory/inject-context.sh`：

```bash
#!/usr/bin/env bash
# pre_llm_call hook — 每次LLM调用前提醒
cat <<'EOF'
{"context": "【系统提醒】如果你准备交付报告/分析/文件，请先执行 pillar-verify 验证。\n未经验证的交付会被 pre_tool_call hook 物理拦截。\n已设置验证标记的方式：touch /tmp/.bazi_verified"}
EOF
```

### post_tool_call 审计脚本（observer only）

保存到 `/root/.hermes/hooks/bazi-mandatory/check.sh`：

```python
#!/usr/bin/env python3
"""
post_tool_call hook — 观察层，记录工具调用日志
注意：返回值被忽略，不能阻断也不能注入。
"""
import sys, json, os
from datetime import datetime

LOG_DIR = os.path.expanduser("~/.hermes/logs/tool_audit")
os.makedirs(LOG_DIR, exist_ok=True)

def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return

    tool_name = payload.get("tool_name", "")
    duration_ms = payload.get("duration_ms", 0)
    args = payload.get("args", {})

    log_entry = {
        "ts": datetime.now().isoformat(),
        "tool": tool_name,
        "duration_ms": duration_ms,
        "path": args.get("path", ""),
    }

    log_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y%m%d')}.jsonl")
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
```

## 正确的交付流程

```bash
# 第1步：跑验证
bash projects/bazi-platform/scripts/pillar-verify.py

# 第2步：设放行标记（告诉hook：已通过验证）
touch /tmp/.bazi_verified

# 第3步：写文件（hook自动检测放行标记）
write_file 或 patch

# 第4步：推库
cd /root/weiwuji-knowledge-base && git add -A && git commit -m "..." && git push
cd /root/.hermes/profiles/jinjian-zhenren && git add -A && git commit -m "..." && git push
```

## 六六一键配置脚本

保存到 `/root/.hermes/hooks/bazi-mandatory/setup-hermes-enterprise.sh`：

```bash
#!/usr/bin/env bash
# 用法: bash setup-hermes-enterprise.sh <profile_name>
set -euo pipefail

PROFILE="${1:-}"
[ -z "$PROFILE" ] && { echo "用法: $0 <profile_name>"; exit 1; }

PROFILE_DIR="$HOME/.hermes/profiles/$PROFILE"
mkdir -p "$PROFILE_DIR" "$PROFILE_DIR/memories"

# 写入 SOUL.md（瘦身版）
cat > "$PROFILE_DIR/SOUL.md" << 'EOF'
# SOUL.md — 身份 + 铁律
## 🪪 我的身份
我是六六，金鉴体系下的协作Agent。
## 🚨 铁律
1. 规则在hooks里物理拦截，不靠自觉
2. 写文件前必须先过验证
3. 每次会话先跑 date 确认时间
4. 汇报时引用具体数据，不说"看起来好了"
EOF

# 写入 config.yaml
cat > "$PROFILE_DIR/config.yaml" << 'CONFIGEOF'
model:
  default: "deepseek/deepseek-chat"
  provider: "openrouter"
hooks:
  pre_tool_call:
    - /root/.hermes/hooks/bazi-mandatory/precheck.sh
  post_tool_call:
    - /root/.hermes/hooks/bazi-mandatory/check.sh
  pre_llm_call:
    - /root/.hermes/hooks/bazi-mandatory/inject-context.sh
hooks_auto_accept: true
tool_use_enforcement: true
CONFIGEOF

echo "✅ 配置完成: $PROFILE"
```

## 关键教训

1. **post_tool_call 返回值被忽略** — 不能做验证拦截，只能做日志审计
2. **pre_tool_call 才能 block** — 返回 `{"action": "block", "message": "..."}`
3. **pre_llm_call 注入到用户消息层** — 不是系统提示，约束力弱
4. **on_session_start 是 observer-only** — 不能注入上下文（网关hooks版可以但plugin/shell不行）
5. **hooks 脚本出错不阻断 Agent** — "All three systems are non-blocking — errors are caught and logged, never crashing the agent"
