#!/bin/bash
# ═══════════════════════════════════════════════
# 金鉴真人·物理门禁自动触发 v1.0
# 用法：
#   写完报告后→ bash run-with-gate.sh 姓名 报告路径 [引擎路径]
#
# 示例：
#   bash run-with-gate.sh 主母成 /tmp/主母成_精要报告_v1.0_20260707.md
#   bash run-with-gate.sh 主母成 /tmp/主母成_精要报告_v1.0_20260707.md /tmp/主母成_engine.json
#
# 行为：
#   1. 跑 delivery-gate.py
#   2. PASS → 绿色 ✅ 并自动继续
#   3. FAIL → 红色 ❌ 并退出（必须先修）
# ═══════════════════════════════════════════════

NAME="${1:-}"
REPORT="${2:-}"
ENGINE="${3:-/tmp/${NAME}_engine.json}"

if [ -z "$NAME" ] || [ -z "$REPORT" ]; then
    echo "用法：bash run-with-gate.sh 姓名 报告路径 [引擎路径]"
    echo "示例：bash run-with-gate.sh 主母成 /tmp/主母成_精要报告_v1.0_20260707.md"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GATE="${SCRIPT_DIR}/delivery-gate.py"

if [ ! -f "$GATE" ]; then
    echo "❌ 门禁脚本不存在：$GATE"
    echo "   请先创建 delivery-gate.py"
    exit 1
fi

if [ ! -f "$REPORT" ]; then
    echo "❌ 报告文件不存在：$REPORT"
    exit 1
fi

ENGINE_ARG=""
if [ -f "$ENGINE" ]; then
    ENGINE_ARG="--engine $ENGINE"
fi

echo ""
echo "═══════════════════════════════════════════"
echo "🔒 金鉴真人·交付物理门禁"
echo "   报告：$REPORT"
echo "   引擎：${ENGINE:-无}"
echo "═══════════════════════════════════════════"
echo ""

python3 "$GATE" --report "$REPORT" $ENGINE_ARG --verbose

EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "═══════════════════════════════════════════"
    echo "✅✅✅ 门禁通过！可以交付给老板。"
    echo "═══════════════════════════════════════════"
    exit 0
else
    echo ""
    echo "═══════════════════════════════════════════"
    echo "⛔⛔⛔ 门禁阻断！先修复再重跑。"
    echo "     bash run-with-gate.sh $NAME \"$REPORT\""
    echo "═══════════════════════════════════════════"
    exit 1
fi
