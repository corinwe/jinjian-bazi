#!/bin/bash
#===============================================================================
# 金鉴真人·Sub Agent 回写校验脚本 bazi-delegate-check.sh v1.0
# 功能：delegate_task 返回后自动检查子 agent 输出质量
# 用法：bash bazi-delegate-check.sh <报告路径> [姓名] [出生年]
# 返回：0=通过 / 1=不通过 / 2=文件不存在
#===============================================================================

if [ $# -lt 1 ]; then
    echo "用法: bash bazi-delegate-check.sh <报告路径> [姓名] [出生年]"
    echo "例: bash bazi-delegate-check.sh ./子源_v20.0.md 子源 2011"
    exit 2
fi

REPORT="$1"
NAME="${2:-}"
BIRTH_YEAR="${3:-}"

echo "╔════════════════════════════════════════════════╗"
echo "║  金鉴真人·Sub Agent回写校验 v1.0              ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# 1. 文件存在性
if [ ! -f "$REPORT" ]; then
    echo "❌ 文件不存在: $REPORT"
    echo "→ 子 agent 可能未生成报告，需重新发起任务"
    exit 2
fi

SIZE=$(stat -c%s "$REPORT" 2>/dev/null || echo 0)
LINES=$(wc -l < "$REPORT" 2>/dev/null || echo 0)

echo "文件: $REPORT"
echo "大小: ${SIZE}字节"
echo "行数: ${LINES}行"

PASS=0
FAIL=0

check() {
    local desc="$1"
    local result="$2"
    if [ "$result" = "true" ] || [ "$result" -eq 0 ] 2>/dev/null; then
        echo "  ✅ $desc"
        PASS=$((PASS+1))
    else
        echo "  ❌ $desc"
        FAIL=$((FAIL+1))
    fi
}

echo ""
echo "--- 存在性检查 ---"
check "文件存在" "true"
check "文件大小 > 10KB" "$( [ $SIZE -gt 10240 ] && echo true || echo false )"

echo ""
echo "--- 深度检查 ---"
check "行数 ≥ 1,500行" "$( [ $LINES -ge 1500 ] && echo true || echo false )"
check "行数 ≥ 1,700行（达标）" "$( [ $LINES -ge 1700 ] && echo true || echo false )"

echo ""
echo "--- §板块完整性 ---"
check "§1 一页总览" "$(grep -cq "§1\|一页总览" "$REPORT" && echo true || echo false)"
check "§8 财富分析" "$(grep -cq "§8\|财富分析" "$REPORT" && echo true || echo false)"
check "§16 事件总表" "$(grep -cq "§16\|事件总表\|全生命周期" "$REPORT" && echo true || echo false)"
check "§17 大运精析" "$(grep -cq "§17\|大运精析" "$REPORT" && echo true || echo false)"
check "§18 三决断" "$(grep -cq "§18\|三决断" "$REPORT" && echo true || echo false)"
check "§21 人生建议" "$(grep -cq "§21\|人生建议" "$REPORT" && echo true || echo false)"

# 统计§数量
SECTION_COUNT=$(grep -c "## §" "$REPORT" || echo 0)
check "§板块数 ≥ 19" "$( [ $SECTION_COUNT -ge 19 ] && echo true || echo false )"
check "§板块数 = 21（全量）" "$( [ $SECTION_COUNT -ge 21 ] && echo true || echo false )"

echo ""
echo "--- 关键内容检查 ---"

check "补财库方案（§8.5）" "$(grep -cq "补财库\|财库检查\|蓄财策略" "$REPORT" && echo true || echo false)"
check "理论来源标注【金鉴真人·§】" "$(grep -cq "金鉴真人·§" "$REPORT" && echo true || echo false)"
check "关键年份类型标记" "$(grep -cq '【学业】\|【事业】\|【财富】\|【健康】' "$REPORT" && echo true || echo false)"

# 文昌检查（仅限未成年人）
if [ -n "$BIRTH_YEAR" ] && [ "$BIRTH_YEAR" -ge 2001 ] 2>/dev/null; then
    check "补文昌判断（未成年强制）" "$(grep -cq "是否需要补文昌\|补文昌判断" "$REPORT" && echo true || echo false)"
    check "文昌方案（未成年强制）" "$(grep -cq "文昌改进方案\|文昌布局" "$REPORT" && echo true || echo false)"
fi

# 姓名分析检查（仅限有姓名时）
if [ -n "$NAME" ]; then
    check "姓名五行分析（如有姓名）" "$(grep -cq "姓名五行\|笔画数" "$REPORT" && echo true || echo false)"
fi

echo ""
echo "════════════════════════════════════════════════"
echo "通过: $PASS / 失败: $FAIL"

if [ $FAIL -gt 0 ]; then
    echo "❌ 子 agent 输出不达标，需修正或重跑"
    exit 1
else
    echo "✅ 子 agent 输出达标！"
    exit 0
fi
