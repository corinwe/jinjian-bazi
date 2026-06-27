#!/bin/bash
# ═══════════════════════════════════════════════════════
# 金鉴真人·DevOps 一键加固脚本
# 安装: ./setup-devops.sh
# 验证: ./setup-devops.sh --check
# ═══════════════════════════════════════════════════════

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
PASS=0
FAIL=0

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

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

# ── 参数处理 ──
if [ "${1:-}" = "--check" ]; then
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}  金鉴真人·DevOps 状态检查${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"

    section "工具安装"
    check "ruff"               "which ruff && ruff --version"
    check "pytest"             "which pytest && pytest --version"
    check "pytest-cov"         "python3 -c 'import pytest_cov'"
    check "pre-commit"         "which pre-commit && pre-commit --version"
    check "mypy"               "which mypy && mypy --version"

    section "Pre-commit Hooks"
    check "git hooks installed" "ls .git/hooks/pre-commit 2>/dev/null"
    check "pre-push hooks"      "ls .git/hooks/pre-push 2>/dev/null"

    section "项目配置"
    check "pyproject.toml"      "test -f pyproject.toml"
    check "pre-commit-config"   "test -f .pre-commit-config.yaml"
    check "CI/CD workflow"      "test -f .github/workflows/ci-cd.yml"
    check "Dockerfile"          "test -f Dockerfile"

    section "自动测试"
    check "import验证"          "cd engine && python3 tests/test_imports.py >/dev/null 2>&1"
    check "320条引擎测试"       "cd engine && python3 tests/test_full_suite.py >/dev/null 2>&1"

    section "服务状态"
    check "API /ping"           "curl -sf http://localhost:8000/ping >/dev/null 2>&1 || curl -sf http://43.162.90.39:8000/ping >/dev/null 2>&1"
    check "API /health"         "curl -sf http://localhost:8000/health >/dev/null 2>&1 || curl -sf http://43.162.90.39:8000/health >/dev/null 2>&1"

    echo ""
    echo -e "结果: ${GREEN}${PASS}通过${NC} ${RED}${FAIL}失败${NC} / $((PASS+FAIL))总项"
    [ "$FAIL" -eq 0 ] && exit 0 || exit 1
fi

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  金鉴真人·DevOps 一键加固${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"

# ── 1. 安装工具 ──
section "1/5 安装工具"
echo "  安装 ruff/pytest-cov/pre-commit/mypy/black..."
pip3 install ruff pytest pytest-cov pre-commit mypy black --break-system-packages -q
echo -e "  ${GREEN}✓${NC} 工具安装完成"

# ── 2. 配置 pre-commit hooks ──
section "2/5 配置 Git Hooks"
pre-commit install 2>/dev/null && echo -e "  ${GREEN}✓${NC} pre-commit hook 已安装"
pre-commit install --hook-type pre-push 2>/dev/null && echo -e "  ${GREEN}✓${NC} pre-push hook 已安装"

# ── 3. 运行 lint + format ──
section "3/5 代码质量扫描"
echo "  运行 ruff lint (autofix)..."
ruff check --fix . 2>/dev/null && echo -e "  ${GREEN}✓${NC} ruff lint 通过" || echo -e "  ${YELLOW}⚠${NC} ruff lint 有残留警告"
echo "  运行 ruff format..."
ruff format . 2>/dev/null && echo -e "  ${GREEN}✓${NC} ruff format 通过"

# ── 4. 运行测试 + 覆盖率 ──
section "4/5 测试 + 覆盖率"
cd engine
python3 tests/test_imports.py && echo -e "  ${GREEN}✓${NC} 模块导入验证"
python3 tests/test_full_suite.py && echo -e "  ${GREEN}✓${NC} 引擎320条测试"
cd "$SCRIPT_DIR"
python3 -m pytest engine/tests/test_full_suite.py --cov=engine --cov-report=term --cov-fail-under=45 -q 2>/dev/null && echo -e "  ${GREEN}✓${NC} 覆盖率基线 (≥45%)"

# ── 5. 服务健康检查 ──
section "5/5 服务健康检查"
for url in "http://localhost:8000/ping" "http://43.162.90.39:8000/ping"; do
    if curl -sf "$url" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $url"
        break
    fi
done

echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ DevOps 加固完成!${NC}"
echo -e "${GREEN}  提交前自动: lint → format → import验证${NC}"
echo -e "${GREEN}  Push前自动: 全量测试 + 覆盖率门禁${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
