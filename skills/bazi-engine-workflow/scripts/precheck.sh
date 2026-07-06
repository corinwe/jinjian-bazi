#!/bin/bash
# ============================================================
# bazi-mandatory pre_tool_call hook（stub）
# 安装路径：/root/.hermes/hooks/bazi-mandatory/precheck.sh
# 触发时机：每次 tool call 前自动执行
# ============================================================
# TODO: 扩展拦截逻辑
# - 拦截 python3 bazi-engine.py（禁止绕过 pipeline 直接排盘）
# - 拦截手动 git push 到知识库（必须走 pipeline --push）
# - 拦截 sed 全局替换（防误改年柱）
set -euo pipefail

exit 0
