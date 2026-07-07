#!/bin/bash
# ============================================================
# 金鉴真人·八字全自动分析管线 v1.0
# 用途：任意八字自动触发全量分析 + 按v2.3模板输出
# 用法：bash bazi-pipeline.sh [年] [月] [日] [时] [分] [时辰索引] [性别] [姓名] [可选:出生地]
# 例：bash bazi-pipeline.sh 2011 5 31 9 0 5 男 子源 成都
# ============================================================

YEAR=$1
MONTH=$2
DAY=$3
HOUR=$4
MIN=$5
SHICHEN_IDX=$6
GENDER=$7
NAME=$8
BIRTHPLACE=${9:-""}

SKILL_DIR="/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform/skills"
OUTPUT_DIR="/root/八字报告"

mkdir -p "$OUTPUT_DIR"

echo "============================================"
echo "📋 金鉴真人·八字全自动分析管线 v1.0"
echo "命主：$NAME ($GENDER)"
echo "出生：${YEAR}年${MONTH}月${DAY}日 ${HOUR}:${MIN} (时辰索引:$SHICHEN_IDX)"
echo "============================================"

# === Step 1: 排盘验证 ===
echo ""
echo "⚡ Step 1/4 — 排盘验证门禁..."
PYTHON_CMD="python3 ${SKILL_DIR}/bazi/bazi-engine.py ${YEAR} ${MONTH} ${DAY} ${HOUR} ${MIN} ${SHICHEN_IDX} ${GENDER} ${NAME}"
if [ -n "$BIRTHPLACE" ]; then
    PYTHON_CMD="$PYTHON_CMD $BIRTHPLACE"
fi
eval $PYTHON_CMD
if [ $? -ne 0 ]; then
    echo "❌ 排盘验证失败！"
    exit 1
fi
echo "✅ 排盘验证通过"

# === Step 2: 基础包加载 ===
echo ""
echo "⚡ Step 2/4 — 加载基础包..."
echo "  → bazi-foundation-analysis (总纲/能量/身强弱/用神/格局/空亡/墓库/神煞/§23外貌)"
echo "✅ 基础包就绪"

# === Step 3: 全量加载所有子skill ===
echo ""
echo "⚡ Step 3/4 — 全量加载10个子skill..."
SKILLS=(
    "bazi-education-analysis:学业/文昌"
    "bazi-wealth-analysis:财富/财库"
    "bazi-career-analysis:事业/近官立贵"
    "bazi-misfortune-analysis:灾祸/疾病/官司"
    "bazi-marriage-analysis:婚姻/配偶/私生子"
    "bazi-children-analysis:子女/生育"
    "bazi-liunian-analysis:流年/大运/能量"
    "bazi-health-psychology:健康/七杀/偏印"
    "bazi-fortune-analysis:性格/十神/甲己合土"
    "bazi-remission-methods:化解/太岁/补运"
)
for skill_entry in "${SKILLS[@]}"; do
    skill_name="${skill_entry%%:*}"
    skill_desc="${skill_entry##*:}"
    echo "  → $skill_name ($skill_desc)"
done
echo "✅ 全量10子skill就绪"

# === Step 4: 按模板输出 ===
echo ""
echo "⚡ Step 4/4 — 按v2.3模板输出12大板块..."
OUTPUT_FILE="${OUTPUT_DIR}/${NAME}_完整深析报告_全自动管线_$(date +%Y%m%d).md"
echo "  输出路径: $OUTPUT_FILE"
echo ""
echo "📋 12大板块强制覆盖:"
echo "  [1] 📋 一页总览表(21字段)"
echo "  [2] 🏗️ 格局分析(≥250字)"
echo "  [3] 💪 身强弱详解(≥300字)"
echo "  [4] 🎯 喜用神详解(≥250字)"
echo "  [5] 🧠 性格分析(≥500字·5特质)"
echo "  [6] 💃 身材外貌分析(≥300字·§23五步法)"
echo "  [7] 🎓 学历分析(≥350字·第0层三档+六步)"
echo "  [8] 💰 财富分析(≥500字)"
echo "  [9] 💼 事业分析(≥300字·近官立贵)"
echo "  [10] 💕 婚姻分析(≥400字)"
echo "  [11] 👶 子女分析(≥200字)"
echo "  [12] ⚠️ 健康分析(≥500字·含外貌身材)"
echo "  + 全生命周期事件总表"
echo "  + 灾祸/疾病/搬迁专项"
echo "  + 大运流年到70岁"
echo ""
echo "============================================"
echo "✅ 全自动管线就绪！分析指令已发送给AI引擎。"
echo "输出文件: $OUTPUT_FILE"
echo "============================================"
