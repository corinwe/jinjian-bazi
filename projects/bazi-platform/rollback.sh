#!/bin/bash
# ═══════════════════════════════════════════════════════
# 金鉴真人·一键回滚脚本
# 用法: ./rollback.sh          → 回滚到上一版本
#       ./rollback.sh <n>      → 回滚到前n个版本
#       ./rollback.sh <commit> → 回滚到指定commit
#       ./rollback.sh --list   → 查看部署历史
# ═══════════════════════════════════════════════════════

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

HISTORY_FILE="$SCRIPT_DIR/.deploy-history"
BAZI_DIR="/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform"

# ── 查看部署历史 ──
if [ "${1:-}" = "--list" ] || [ "${1:-}" = "-l" ]; then
    echo -e "${GREEN}═══ 部署历史 ═══${NC}"
    if [ ! -f "$HISTORY_FILE" ]; then
        echo "  暂无部署历史记录"
    else
        nl -w 3 "$HISTORY_FILE"
    fi
    exit 0
fi

# ── 确定回滚目标 ──
if [ $# -eq 0 ]; then
    # 回退到上一个版本
    TARGET="HEAD~1"
    LABEL="上一版本"
elif [[ "$1" =~ ^[0-9]+$ ]]; then
    TARGET="HEAD~$1"
    LABEL="前 $1 个版本"
else
    TARGET="$1"
    LABEL="commit $1"
fi

echo -e "${YELLOW}⚠️  即将回滚到 $LABEL${NC}"
echo -e "${YELLOW}  目标: $TARGET${NC}"
echo ""
echo -e "  部署前会:"
echo -e "  1. 记录当前版本 (用于再次回滚)"
echo -e "  2. git reset --hard 到目标版本"
echo -e "  3. 重新安装依赖"
echo -e "  4. 运行引擎验证"
echo -e "  5. 重启服务"
echo -e "  6. 健康检查"
echo ""
read -p "  确认回滚? [y/N] " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "  已取消"
    exit 0
fi

# ── 执行回滚 ──
cd "$BAZI_DIR"
CURRENT_COMMIT=$(git rev-parse --short HEAD)

echo -e "${YELLOW}[1/6]${NC} 记录当前版本..."
echo "ROLLBACK_FROM: $(date +%Y%m%d_%H%M%S) $CURRENT_COMMIT" >> "$HISTORY_FILE"

echo -e "${YELLOW}[2/6]${NC} 回滚代码到 $LABEL..."
git reset --hard "$TARGET"
ROLLBACK_COMMIT=$(git rev-parse --short HEAD)
echo "  当前: $ROLLBACK_COMMIT"

echo -e "${YELLOW}[3/6]${NC} 安装依赖..."
pip3 install -r api/requirements.txt --break-system-packages -q
echo -e "  ${GREEN}✓${NC}"

echo -e "${YELLOW}[4/6]${NC} 验证引擎..."
cd engine
python3 tests/test_imports.py
python3 tests/test_full_suite.py
cd "$BAZI_DIR"
echo -e "  ${GREEN}✓${NC}"

echo -e "${YELLOW}[5/6]${NC} 重启服务..."
pkill -f 'uvicorn api.main' 2>/dev/null || true
sleep 1
nohup python3 -m uvicorn api.main:app \
    --host 0.0.0.0 --port 8000 \
    --log-level warning > /tmp/bazi-api.log 2>&1 &
sleep 3

echo -e "${YELLOW}[6/6]${NC} 健康检查..."
curl -sf http://localhost:8000/ping | grep -q 'ok' && echo -e "  ${GREEN}✓${NC} ping OK"
curl -sf http://localhost:8000/health | grep -q 'healthy' && echo -e "  ${GREEN}✓${NC} health OK"

echo ""
echo -e "  ✅ 回滚完成: ${GREEN}$CURRENT_COMMIT${NC} → ${GREEN}$ROLLBACK_COMMIT${NC}"
echo ""
echo "  记录已写入: $HISTORY_FILE"
