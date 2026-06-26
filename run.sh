#!/bin/bash
# ═══════════════════════════════════════════════════════
# 金鉴真人·八字命理分析平台 — 启动脚本
# 一键启动API服务（含前端）
# ═══════════════════════════════════════════════════════

set -e

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  金鉴真人·八字命理分析平台 v5.0${NC}"
echo -e "${GREEN}  确定性规则引擎 | 21§完整输出${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"

# ── 检查依赖 ──
echo -ne "${YELLOW}[1/4]${NC} 检查运行环境..."
PYTHON_OK=$(python3 -c "import fastapi, uvicorn, sqlite3; print('OK')" 2>/dev/null)
if [ "$PYTHON_OK" != "OK" ]; then
    echo -e " ${RED}✗${NC}"
    echo "缺少Python依赖。执行: pip3 install -r api/requirements.txt"
    exit 1
fi
echo -e " ${GREEN}✓${NC}"

# ── 检查引擎 ──
echo -ne "${YELLOW}[2/4]${NC} 验证规则引擎..."
cd "$SCRIPT_DIR/engine"
python3 -c "
import sys
sys.path.insert(0, '.')
from pipeline_v5 import run_pipeline
from constants import BaZi, Pillar
from shen_qiang_ruo import compute_shen_qiang_ruo
from cai_xing import compute_cai_xing
# 快速验证: 家主题
bazi = BaZi(year=Pillar('庚','申'), month=Pillar('癸','未'),
             day=Pillar('辛','亥'), hour=Pillar('辛','卯'), gender='男')
s, l, _ = compute_shen_qiang_ruo(bazi)
c = compute_cai_xing(bazi)
assert s == 64.0, f'身强分数期望64.0, 实际{s}'
assert c.total == 31.2, f'财星期望31.2, 实际{c.total}'
print('OK')
" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e " ${RED}✗${NC}"
    echo "引擎验证失败。"
    exit 1
fi
echo -e " ${GREEN}✓${NC}"

# ── 数据库 ──
echo -ne "${YELLOW}[3/4]${NC} 初始化数据库..."
cd "$SCRIPT_DIR"
python3 -c "
import os, sys
sys.path.insert(0, '.')
from database.connection import init_db
init_db()
print('OK')
" 2>/dev/null
echo -e " ${GREEN}✓${NC}"

# ── 启动服务 ──
echo -ne "${YELLOW}[4/4]${NC} 启动API服务..."
cd "$SCRIPT_DIR"

HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-8000}

echo -e " ${GREEN}✓${NC}"
echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "  服务地址: http://${HOST}:${PORT}"
echo -e "  API文档:  http://${HOST}:${PORT}/docs"
echo -e "  前端:     http://${HOST}:${PORT}/"
echo -e "  引擎:     ${SCRIPT_DIR}/engine/ (12,437行)"
echo -e "  测试:     ${SCRIPT_DIR}/engine/tests/test_full_suite.py"
echo -e "  日志:     Ctrl+C 停止服务"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""

export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

exec python3 -m uvicorn api.main:app \
    --host "$HOST" \
    --port "$PORT" \
    --reload \
    --log-level info
