#!/bin/bash
# ═══════════════════════════════════════════════════════════
# 金鉴真人 · 排盘强制门禁脚本
# 任何八字分析前必须先运行本脚本，禁止手算排盘
# 铁律来源: credentials.md → 铁律①（2026-06-29固化）
# ═══════════════════════════════════════════════════════════

ENGINE_DIR="/root/bazi-platform/engine"
CONFIG_FILE="/root/bazi-platform/.hermes/config/credentials.md"

echo "════════════════════════════════════════"
echo "🔒 金鉴真人 · 排盘强制门禁"
echo "════════════════════════════════════════"

# 检查1：引擎是否存在
if [ ! -f "$ENGINE_DIR/paipan.py" ]; then
    echo "❌ 错误: 引擎 paipan.py 不存在！"
    echo "   路径: $ENGINE_DIR/paipan.py"
    exit 1
fi

# 检查2：config是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 错误: 项目配置不存在！"
    echo "   路径: $CONFIG_FILE"
    exit 1
fi

# 用法
usage() {
    echo ""
    echo "用法: $0 -n <姓名> -g <男/女> -y <年> -m <月> -d <日> -h <时>"
    echo ""
    echo "示例: $0 -n 梦 -g 女 -y 2007 -m 7 -d 27 -h 5"
    echo ""
    echo "输出: 引擎排盘结果（JSON格式）"
    echo "      必须基于此数据进行后续分析"
    echo ""
    exit 1
}

# 解析参数
while getopts "n:g:y:m:d:h:" opt; do
    case $opt in
        n) NAME="$OPTARG" ;;
        g) GENDER="$OPTARG" ;;
        y) YEAR="$OPTARG" ;;
        m) MONTH="$OPTARG" ;;
        d) DAY="$OPTARG" ;;
        h) HOUR="$OPTARG" ;;
        *) usage ;;
    esac
done

if [ -z "$NAME" ] || [ -z "$GENDER" ] || [ -z "$YEAR" ] || [ -z "$MONTH" ] || [ -z "$DAY" ]; then
    usage
fi

if [ -z "$HOUR" ]; then
    echo "⚠️  未指定时辰，将计算所有12个时辰"
fi

echo ""
echo "📋 排盘参数: $NAME | $GENDER | ${YEAR}年${MONTH}月${DAY}日 ${HOUR}时"
echo ""

# 运行引擎排盘
cd "$ENGINE_DIR"

# 如果有时辰，用 pipeline_v5 或 paipan
if [ -n "$HOUR" ]; then
    python3 -c "
import sys
sys.path.insert(0, '.')
from paipan import get_full_paipan
from datetime import date
import json

result = get_full_paipan($YEAR, $MONTH, $DAY, $HOUR, '$GENDER')
result['_gate_verified'] = True
result['_gate_timestamp'] = '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
result['_gate_rule'] = '铁律①: 排盘必须跑引擎，禁止手算（2026-06-29固化）'
print(json.dumps(result, ensure_ascii=False, indent=2))
" 2>&1

    EXIT_CODE=$?
    if [ $EXIT_CODE -ne 0 ]; then
        echo ""
        echo "❌ 引擎排盘失败！请检查输入参数"
        exit 1
    fi
else
    # 无时辰，遍历12个时辰
    echo "⚠️  无时辰参数，输出12个时辰的排盘结果："
    for shi in 子丑寅卯辰巳午未申酉戌亥; do
        python3 -c "
import sys
sys.path.insert(0, '.')
from paipan import get_full_paipan
from datetime import date
import json

# 时辰映射
SHI_MAP = {'子':0,'丑':2,'寅':4,'卯':6,'辰':8,'巳':10,'午':12,'未':14,'申':16,'酉':18,'戌':20,'亥':22}
result = get_full_paipan($YEAR, $MONTH, $DAY, SHI_MAP['$shi'], '$GENDER')
print(f\"\$shi时: {result['bazi']} | 日主: {result['ri_zhu']} | 时柱: {result['hour']['gan']}{result['hour']['zhi']}\")
"
    done
fi

echo ""
echo "✅ 门禁通过 — 排盘数据来自引擎，非手算"
echo "⚠️  后续分析必须基于上述引擎输出，不可自行重算日柱"
echo "════════════════════════════════════════"
