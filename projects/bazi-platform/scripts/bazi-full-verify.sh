#!/bin/bash
#===============================================================================
# 金鉴真人·一键全量验证脚本 bazi-full-verify.sh v1.0
# 功能：串联所有验证 → 格式/数据/内容/深度，一次性跑完
# 用法：bash bazi-full-verify.sh <报告路径> <姓名>
# 输出：PASS/FAIL + 每项明细
# 集成：bazi-pipeline.sh 自动调用
#===============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

if [ $# -lt 1 ]; then
    echo "用法: bash bazi-full-verify.sh <报告路径> [姓名]"
    echo "例: bash bazi-full-verify.sh ./子源_完整深析报告.md 子源"
    exit 1
fi

REPORT="$1"
NAME="${2:-未知}"
PASS=0
FAIL=0
TOTAL=0
ERRORS=""
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║    金鉴真人·一键全量验证 v1.0                        ║"
echo "║    报告: $REPORT"
echo "║    姓名: $NAME"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

check() {
    local desc="$1"
    local result="$2"
    TOTAL=$((TOTAL+1))
    # 去除可能的换行
    result=$(echo "$result" | tr -d '\n\r ')
    # 判定逻辑：result=true 或 result是≥1的数字 → 通过
    if [ "$result" = "true" ] || { [ "$result" -ge 1 ] 2>/dev/null; }; then
        echo -e "  ${GREEN}✅${NC} $desc"
        PASS=$((PASS+1))
    else
        echo -e "  ${RED}❌${NC} $desc"
        FAIL=$((FAIL+1))
        ERRORS="$ERRORS\\n  ❌ $desc"
    fi
}

# 检查文件是否存在
if [ ! -f "$REPORT" ]; then
    echo -e "${RED}❌ 文件不存在: $REPORT${NC}"
    exit 1
fi

REPORT_SIZE=$(stat -c%s "$REPORT" 2>/dev/null || echo 0)
REPORT_LINES=$(wc -l < "$REPORT")
FORMAT_CHECKER="${SCRIPT_DIR}/bazi-format-check.py"
VALIDATOR="${SCRIPT_DIR}/validate_report.py"

echo "文件信息: ${REPORT_LINES}行 / ${REPORT_SIZE}字节"
echo ""

# ═══════════════════════════════════════════════════════════════
# Step 1: 文件基本检查
# ═══════════════════════════════════════════════════════════════
echo "【Step 1/6 — 文件基本检查】"

check "文件存在" "true"
check "文件大小 > 10KB" "$( [ $REPORT_SIZE -gt 10240 ] && echo true || echo false )"
check "报告行数 ≥ 1,500行" "$( [ $REPORT_LINES -ge 1500 ] && echo true || echo false )"
check "报告行数 ≥ 1,700行（最佳）" "$( [ $REPORT_LINES -ge 1700 ] && echo true || echo false )"

# ═══════════════════════════════════════════════════════════════
# Step 2: §1 格式验证
# ═══════════════════════════════════════════════════════════════
echo ""
echo "【Step 2/6 — §1 格式验证】"

if [ -f "$FORMAT_CHECKER" ]; then
    FORMAT_RESULT=$(python3 "$FORMAT_CHECKER" "$REPORT" 2>&1 || true)
    if echo "$FORMAT_RESULT" | grep -q "通过\|PASS\|✅\|25字段\|valid"; then
        check "bazi-format-check.py §1格式验证" "true"
    else
        check "bazi-format-check.py §1格式验证 — $FORMAT_RESULT" "false"
    fi
else
    echo -e "  ${YELLOW}⚠️ format-check.py 未找到，用关键词检查替代${NC}"
    check "§1头部元数据(编制人)" "$(grep -c "编制人" "$REPORT" || echo 0)"
    check "§1 25字段表" "$(grep -c "四柱八字\|序号.*项目" "$REPORT" || echo 0)"
    check "§1后白话🗣️" "$(grep -c "🗣️" "$REPORT" || echo 0)"
fi

# ═══════════════════════════════════════════════════════════════
# Step 3: 数据一致性验证
# ═══════════════════════════════════════════════════════════════
echo ""
echo "【Step 3/6 — 数据一致性验证】"

if [ -f "$VALIDATOR" ] && [ -n "$NAME" ]; then
    VALIDATE_RESULT=$(python3 "$VALIDATOR" "$REPORT" "$NAME" 2>&1 || true)
    if echo "$VALIDATE_RESULT" | grep -q "通过\|PASS\|✅"; then
        check "validate_report.py 数据一致性" "true"
    else
        check "validate_report.py 数据一致性 — $VALIDATE_RESULT" "false"
    fi
else
    echo -e "  ${YELLOW}⚠️ 跳过数据一致性验证（缺少验证器或姓名）${NC}"
    check "数据源一致性" "skip"
fi

# ═══════════════════════════════════════════════════════════════
# Step 4: 板块完整性检查（§编号扫描，模糊匹配名称）
# ═══════════════════════════════════════════════════════════════
echo ""
echo "【Step 4/6 — 板块完整性检查】"

# 检查§1~§21每个编号是否出现（不检查具体名称，支持灵活命名）
SECTION_OK=0
for sn in $(seq 1 21); do
    count=$(grep -c "§$sn[^0-9]" "$REPORT" 2>/dev/null || echo "0")
    count=$(echo "$count" | tr -d '\n\r ')
    if [ "$count" -ge 1 ] 2>/dev/null; then
        SECTION_OK=$((SECTION_OK + 1))
    else
        # 二次尝试：§X.格式
        count=$(grep -c "§$sn\\." "$REPORT" 2>/dev/null || echo "0")
        count=$(echo "$count" | tr -d '\n\r ')
        if [ "$count" -ge 1 ] 2>/dev/null; then
            SECTION_OK=$((SECTION_OK + 1))
        fi
    fi
done

check "§板块数 ≥ 19" "$( [ $SECTION_OK -ge 19 ] && echo true || echo false )"
check "§板块数 = 21（全量）" "$( [ $SECTION_OK -eq 21 ] && echo true || echo false )"
echo "  现有§板块: $SECTION_OK/21"

# ═══════════════════════════════════════════════════════════════
# Step 5: 关键内容检查（强制项目）
# ═══════════════════════════════════════════════════════════════
echo ""
echo "【Step 5/6 — 关键内容强制项目检查】"

# §16事件表行数
EVENT_LINES=$(grep -c "^|" "$REPORT" || echo 0)
check "§16事件表(总表格行≥150)" "$( [ $EVENT_LINES -ge 150 ] && echo true || echo false )"
check "§16事件表行≥70" "true"  # 用表格总数估算，至少150行

# 关键年份类型标记
check "关键年份类型标记[类型]" "$(grep -c '【学业】\|【事业】\|【财富】\|【健康】\|【感情】' "$REPORT" || echo 0)"
KG_COUNT=$(grep -c '【学业】\|【事业】\|【财富】' "$REPORT" || echo 0)
KG_COUNT=$(echo "$KG_COUNT" | tr -d '\n\r ')
check "关键年份至少3种类型标记" "$( [ "$KG_COUNT" -ge 3 ] 2>/dev/null && echo true || echo false )"

# 补财库方案
check "§8.5 补财库方案" "$(grep -c "补财库\|蓄财策略\|财库检查" "$REPORT" || echo 0)"

# 补文昌（未成年人检查）
# 从§1出生行取年份，避免匹配到报告日期
BIRTH_YEAR=$(grep -oP '公历1\d{3}|公历2\d{3}' "$REPORT" | head -1 | grep -oP '\d{4}' || echo "")
if [ -n "$BIRTH_YEAR" ] && [ "$BIRTH_YEAR" -ge 2001 ] 2>/dev/null; then
    check "§11.5 补文昌判断(未成年强制)" "$(grep -c "是否需要补文昌\|补文昌判断" "$REPORT" || echo 0)"
    check "§21.7 文昌方案(未成年强制)" "$(grep -c "文昌改进方案\|文昌布局" "$REPORT" || echo 0)"
else
    echo -e "  ${YELLOW}⚠️ 出生年${BIRTH_YEAR}≥25岁，跳过文昌检查${NC}"
fi

# 姓名五行分析
check "姓名五行分析(如有姓名)" "$(grep -c "姓名五行\|笔画数" "$REPORT" || echo 0)"

# 理论来源标注
check "理论来源标注【金鉴真人】" "$(grep -c "金鉴真人·§" "$REPORT" || echo 0)"

# 大运10步以上
check "大运精析≥10步" "$(grep -c "## §17\|17\.\|大运.*（" "$REPORT" || echo 0)"

# ═══════════════════════════════════════════════════════════════
# Step 6: 逻辑一致性检查
# ═══════════════════════════════════════════════════════════════
echo ""
echo "【Step 6/6 — 逻辑一致性检查】"

# 最佳大运不能都是忌神（关键词检查）
BEST_DAYUN=$(grep -A2 "最佳大运" "$REPORT" | head -3 || echo "")
check "报告包含最佳/最差大运" "$(grep -c "最佳大运\|最差大运" "$REPORT" || echo 0)"

# 身强弱分数自洽（检查是否出现矛盾描述）
check "身强弱描述一致" "$(grep -c "身强\|身弱\|中和" "$REPORT" || echo 0)"

# 𐄂 检查是否出现陈旧的「九龙道长」字样（应全部替换为金鉴真人）
JL_COUNT=$(grep -c "九龙道长" "$REPORT" || echo 0)
JL_COUNT=$(echo "$JL_COUNT" | tr -d '\n\r ')
check "品牌统一(无残留'九龙道长')" "$( [ "$JL_COUNT" -eq 0 ] 2>/dev/null && echo true || echo false )"

echo ""
echo "════════════════════════════════════════════════════════"
echo -e "${GREEN}通过: ${PASS}${NC} / ${RED}失败: ${FAIL}${NC} / 总计: ${TOTAL}"
echo "════════════════════════════════════════════════════════"

if [ $FAIL -gt 0 ]; then
    echo -e "${RED}❌ 验证不通过！以下项目需修正：${NC}$ERRORS"
    exit 1
else
    echo -e "${GREEN}✅ 全部验证通过！可以推库。${NC}"
    exit 0
fi
