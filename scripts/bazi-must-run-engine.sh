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
    echo "用法: $0 -n <姓名> -g <男/女> -y <年> -m <月> -d <日> -h <时> [-w]"
    echo ""
    echo "示例: $0 -n 梦 -g 女 -y 2007 -m 7 -d 27 -h 5"
    echo "      $0 -n 张三 -g 男 -y 1990 -m 1 -d 15 -h 10 -w   (带文昌检查)"
    echo ""
    echo "参数:"
    echo "  -n <姓名>   姓名 (必填)"
    echo "  -g <性别>   性别: 男/女 (必填)"
    echo "  -y <年>     出生年份 (必填)"
    echo "  -m <月>     出生月份 (必填)"
    echo "  -d <日>     出生日期 (必填)"
    echo "  -h <时>     出生时辰 (选填，不填则输出12个时辰)"
    echo "  -w          附带文昌贵人检查 (选填)"
    echo ""
    echo "输出: 引擎排盘结果（JSON格式）"
    echo "      必须基于此数据进行后续分析"
    echo ""
    exit 1
}

# 解析参数
WEN_CHANG_CHECK="0"
while getopts "n:g:y:m:d:h:w" opt; do
    case $opt in
        n) NAME="$OPTARG" ;;
        g) GENDER="$OPTARG" ;;
        y) YEAR="$OPTARG" ;;
        m) MONTH="$OPTARG" ;;
        d) DAY="$OPTARG" ;;
        h) HOUR="$OPTARG" ;;
        w) WEN_CHANG_CHECK="1" ;;
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

# 如果有时辰，用 get_full_paipan + 完整引擎评分
if [ -n "$HOUR" ]; then
    python3 -c "
import sys
sys.path.insert(0, '.')
from paipan import get_full_paipan
from pipeline_v5 import run_v5
from constants import BaZi, Pillar
from datetime import date
import json

# 第1步：排盘
result = get_full_paipan($YEAR, $MONTH, $DAY, $HOUR, '$GENDER', '$NAME')
result['_gate_verified'] = True
result['_gate_timestamp'] = '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
result['_gate_rule'] = '铁律①: 排盘必须跑引擎，禁止手算（2026-06-29固化）'

# 第2步：构建 BaZi 对象并运行完整引擎评分
bazi = BaZi(
    year=Pillar(result['year_pillar']['gan'], result['year_pillar']['zhi']),
    month=Pillar(result['month_pillar']['gan'], result['month_pillar']['zhi']),
    day=Pillar(result['day_pillar']['gan'], result['day_pillar']['zhi']),
    hour=Pillar(result['hour_pillar']['gan'], result['hour_pillar']['zhi']),
    gender='$GENDER'
)
full_result = run_v5(bazi, birth_year=$YEAR, birth_month=$MONTH, birth_day=$DAY)
result['engine_scores'] = {
    'shen_qiang_ruo': {'score': full_result.get('sec_3_shen_qiang_ruo', {}).get('score'), 'label': full_result.get('sec_3_shen_qiang_ruo', {}).get('label')},
    'cai_xing': full_result.get('sec_8_wealth', {}).get('cai_xing_total'),
    'ge_ju': full_result.get('sec_2_ge_ju', {}).get('main'),
    'xi_yong_shen': full_result.get('sec_4_xi_yong', {}).get('xi'),
    'marriage': full_result.get('sec_12_marriage'),
    'da_yun_count': len(full_result.get('sec_17_da_yun_detail', {}).get('list', []))
}

# 文昌检查（引擎已自动计算）
wen_chang = result.get('wen_chang', {})
wc_status = '✅ 原文昌' if wen_chang.get('has_wen_chang') else '⚠️ 需补文昌'
wc_detail = wen_chang.get('detail', '未检')
result['_wen_chang_check'] = wc_status
print(json.dumps(result, ensure_ascii=False, indent=2))
print('')
print('📚 文昌检查: ' + wc_status)
print('   ' + wc_detail)
print('⚙️  引擎评分: 身强弱=' + str(result['engine_scores']['shen_qiang_ruo']['score']) + '分 → ' + result['engine_scores']['shen_qiang_ruo']['label'])
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
SHI_MAP = {'子':0,'丑':2,'寅':4,'卯':6,'辰':8,'巳':10,'午':12,'未':14,'申':16,'酉':18,'戌':20,'亥':22}
result = get_full_paipan($YEAR, $MONTH, $DAY, SHI_MAP['$shi'], '$GENDER')
wc = result.get('wen_chang', {})
wc_mark = '✅' if wc.get('has_wen_chang') else '⚠️'
print(f'{wc_mark} ${shi}时: {result[\"bazi\"]} | 日主: {result[\"ri_zhu\"]} | 文昌: {wc.get(\"detail\", \"-\")}')
" 2>&1
    done
fi

echo ""
echo "✅ 门禁通过 — 排盘数据来自引擎，非手算"
echo "⚠️  后续分析必须基于上述引擎输出，不可自行重算日柱"
echo ""

# ── 文昌贵人详细检查（-w 标志）──
if [ "$WEN_CHANG_CHECK" = "1" ] && [ -n "$HOUR" ]; then
    echo "────────────────────────────────────────"
    echo "📚 文昌贵人检查"
    echo "────────────────────────────────────────"
    python3 -c "
import sys
sys.path.insert(0, '$ENGINE_DIR')
from paipan import get_full_paipan

result = get_full_paipan($YEAR, $MONTH, $DAY, $HOUR, '$GENDER', '$NAME')
wc = result.get('wen_chang', {})
print('  日主: ' + result['day_pillar']['gan'])
print('  文昌地支: ' + str(wc.get('wen_chang_zhi', '-')))
print('  检查结果: ' + wc.get('detail', '未知'))
if not wc.get('has_wen_chang') and wc.get('wen_chang_zhi'):
    print('  💡 建议: 补文昌方位 ' + wc['wen_chang_zhi'])
" 2>&1
    echo "────────────────────────────────────────"
fi

echo "════════════════════════════════════════"
