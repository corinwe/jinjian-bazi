#!/bin/bash
# ═══════════════════════════════════════════════
# 金鉴真人 · 任务前强制加载检查
# 每次新任务开始前，必须跑一次
# 跑完如果任何检查项显示 FAIL，必须先补读再干活
# ═══════════════════════════════════════════════

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "📋 金鉴真人 · 任务前强制加载检查"
echo "========================================"

# --- §1 身份设定 ---
echo ""
echo "§1 [身份设定]"
if [ -f /root/bazi-platform/SOUL.md ]; then
    echo "  ✓ SOUL.md 存在 ($(wc -l < /root/bazi-platform/SOUL.md)行)"
    # 提取关键铁律
    echo -e "  ${YELLOW}关键铁律：$(grep -c '铁律' /root/bazi-platform/SOUL.md)条${NC}"
else
    echo -e "  ${RED}✗ SOUL.md 不存在！${NC}"
fi

# --- §2 老板画像 ---
echo ""
echo "§2 [老板画像]"
if [ -f /root/bazi-platform/USER.md ]; then
    echo "  ✓ USER.md 存在 ($(wc -l < /root/bazi-platform/USER.md)行)"
    echo -e "  ${YELLOW}老板: 魏启令 · 核心教训: $(grep -c '教训' /root/bazi-platform/USER.md)条${NC}"
else
    echo -e "  ${RED}✗ USER.md 不存在！${NC}"
fi

# --- §3 项目配置 ---
echo ""
echo "§3 [项目配置]"
SKILLS_DIR="/root/bazi-platform/skills/software-development/bazi-platform-harness/references"
if [ -f "$SKILLS_DIR/project-config.md" ]; then
    echo "  ✓ project-config.md 存在 ($(wc -l < "$SKILLS_DIR/project-config.md")行)"
else
    echo -e "  ${RED}✗ project-config.md 不存在！${NC}"
fi
if [ -f /root/bazi-platform/.hermes/config/credentials.md ]; then
    echo "  ✓ credentials.md 存在 ($(wc -l < /root/bazi-platform/.hermes/config/credentials.md)行)"
else
    echo -e "  ${RED}✗ credentials.md 不存在！${NC}"
fi

# --- §4 分析技能可用性 ---
echo ""
echo "§4 [分析技能就绪]"
BOOTSTRAP_MD="/root/bazi-platform/BOOTSTRAP.md"
if [ -f "$BOOTSTRAP_MD" ]; then
    echo -e "  ${YELLOW}任务→技能矩阵请查: $BOOTSTRAP_MD${NC}"
    echo "  ✓ BOOTSTRAP.md 存在 ($(wc -l < "$BOOTSTRAP_MD")行)"
else
    echo -e "  ${RED}✗ BOOTSTRAP.md 不存在！${NC}"
fi

# --- §5 校验脚本 ---
echo ""
echo "§5 [校验脚本就绪]"
SCRIPTS_OK=0
for script in bazi-must-run-engine.sh canggan-parse.py pillar-verify.py; do
    if [ -f "/root/bazi-platform/scripts/$script" ]; then
        echo "  ✓ $script 存在"
        SCRIPTS_OK=$((SCRIPTS_OK+1))
    else
        echo -e "  ${RED}✗ $script 不存在！${NC}"
    fi
done

# --- AGENTS.md ---
echo ""
echo "📐 [AGENTS.md - 项目物理铁律]"
if [ -f /root/bazi-platform/AGENTS.md ]; then
    echo "  ✓ AGENTS.md 存在 ($(wc -l < /root/bazi-platform/AGENTS.md)行)"
    echo -e "  ${YELLOW}铁律$(grep -c '铁律' /root/bazi-platform/AGENTS.md)条${NC}"
    grep '铁律' /root/bazi-platform/AGENTS.md | while read -r line; do
        echo "    → $line"
    done
else
    echo -e "  ${RED}✗ AGENTS.md 不存在！${NC}"
fi

echo ""
echo "========================================"
if [ "$SCRIPTS_OK" -ge 3 ]; then
    echo -e "  ${GREEN}✅ 全部就绪，可以开始干活${NC}"
else
    echo -e "  ${RED}⚠️  有文件缺失，请先补读！${NC}"
fi
echo "========================================"
