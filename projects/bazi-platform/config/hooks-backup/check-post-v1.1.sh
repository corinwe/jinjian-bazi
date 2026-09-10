#!/usr/bin/env python3
"""
post_tool_call hook — 观察层 + 格式校验
1. 记录每次工具调用的耗时、结果（审计日志）
2. 校验九龙道长版报告的§顺序是否符合标准模板
"""
import sys, json, os
from datetime import datetime

LOG_DIR = os.path.expanduser("~/.hermes/logs/tool_audit")
os.makedirs(LOG_DIR, exist_ok=True)

# 格式验证（从verify-format.py导入检查逻辑）
FORMAT_SCRIPT = os.path.join(os.path.dirname(__file__), "verify-format.py")

def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return

    tool_name = payload.get("tool_name", "")
    duration_ms = payload.get("duration_ms", 0)
    result = payload.get("result", "")
    # 🚨 2026-09-10 修复：真实 payload 用 tool_input（不是 args）→ 旧写法永远拿不到路径
    args = payload.get("tool_input", None)
    if args is None:
        args = payload.get("args", {})
    args = args or {}

    log_entry = {
        "ts": datetime.now().isoformat(),
        "tool": tool_name,
        "duration_ms": duration_ms,
        "path": args.get("path", ""),
        "result_preview": result[:200] if result else "",
    }

    log_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y%m%d')}.jsonl")
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    # 格式校验：tool_name为write_file/patch才检查
    if tool_name in ("write_file", "patch"):
        try:
            import subprocess
            subprocess.run(
                [sys.executable, FORMAT_SCRIPT],
                input=raw,
                capture_output=True,
                text=True,
                timeout=10
            )
        except Exception:
            pass  # hooks不能崩溃agent

if __name__ == "__main__":
    main()
