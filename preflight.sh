#!/bin/bash
# ═══════════════════════════════════════════════════════
# 金鉴真人·部署前检查清单 (Pre-flight Checklist)
# 每次部署前自动运行，确认系统就绪
# ═══════════════════════════════════════════════════════

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
PASS=0
FAIL=0
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BAZI_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

check() {
    local label="$1" cmd="$2"
    if eval "$cmd" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $label"
        ((PASS++))
    else
        echo -e "  ${RED}✗${NC} $label"
        ((FAIL++))
    fi
}

section() {
    echo -e "\n${YELLOW}═══ $1 ═══${NC}"
}

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  金鉴真人·部署前检查清单${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"

# ── 1. 代码状态 ──
section "1/6 代码状态"
check "无未提交变更" "cd $BAZI_DIR && git status --porcelain | wc -l | grep -q '^0$'"
check "在main分支" "cd $BAZI_DIR && git branch --show-current | grep -q 'main'"
check "与远程同步" "cd $BAZI_DIR && git fetch origin && git rev-parse HEAD | grep -q $(git rev-parse origin/main)"

# ── 2. Python环境 ──
section "2/6 Python环境"
check "Python 3.11+" "python3 --version 2>&1 | grep -q '3.1[1-9]'"
check "fastapi已安装" "python3 -c 'import fastapi' 2>/dev/null"
check "uvicorn已安装" "python3 -c 'import uvicorn' 2>/dev/null"
check "pydantic已安装" "python3 -c 'import pydantic' 2>/dev/null"

# ── 3. 引擎验证 ──
section "3/6 引擎验证"
check "模块导入" "cd $BAZI_DIR/engine && python3 tests/test_imports.py >/dev/null 2>&1"
check "全量测试" "cd $BAZI_DIR/engine && python3 tests/test_full_suite.py >/dev/null 2>&1"
check "覆盖率≥45%" "cd $BAZI_DIR && python3 -m pytest engine/tests/test_full_suite.py --cov=engine --cov-fail-under=45 -q >/dev/null 2>&1"

# ── 4. 代码质量 ──
section "4/6 代码质量"
check "ruff lint通过" "cd $BAZI_DIR && ruff check . -q 2>/dev/null"
check "ruff format检查" "cd $BAZI_DIR && ruff format . --check -q 2>/dev/null"

# ── 5. 基础设施 ──
section "5/6 基础设施"
check "Dockerfile存在" "test -f $BAZI_DIR/Dockerfile"
check "CI/CD配置" "test -f $BAZI_DIR/.github/workflows/ci-cd.yml"
check "pre-commit已安装" "test -f $BAZI_DIR/.git/hooks/pre-commit"
check "pyproject.toml" "test -f $BAZI_DIR/pyproject.toml"

# ── 6. 服务就绪 ──
section "6/6 服务就绪"
# 检查能否启动（但不实际启动）
check "API导入正常" "cd $BAZI_DIR && python3 -c 'import sys; sys.path.insert(0,\".\"); from api.main import app; print(\"OK\")' 2>/dev/null"

# ── 总结 ──
echo ""
TOTAL=$((PASS+FAIL))
echo -e "结果: ${GREEN}${PASS}通过${NC} ${RED}${FAIL}失败${NC} / ${TOTAL}总项"
if [ "$FAIL" -eq 0 ]; then
    echo -e "${GREEN}✅ 全部就绪，可以部署！${NC}"
    exit 0
else
    echo -e "${RED}❌ 有 $FAIL 项未通过，请修复后再部署${NC}"
    exit 1
fi
