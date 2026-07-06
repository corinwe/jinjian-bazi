#!/bin/bash
# ═══════════════════════════════════════════════════════════
# 金鉴真人 · 文昌贵人检查脚本
# 检查八字命局中是否有文昌贵人，以及是否需要补文昌
# ═══════════════════════════════════════════════════════════

ENGINE_DIR="/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform/engine"

echo "════════════════════════════════════════"
echo "📚 金鉴真人 · 文昌贵人检查"
echo "════════════════════════════════════════"

usage() {
    echo ""
    echo "用法: $0 -n <姓名> -r <日主天干> [-z <年支,月支,日支,时支>]"
    echo "                    [-g <年干,月干,日干,时干>]"
    echo ""
    echo "参数:"
    echo "  -n <姓名>         姓名 (必填)"
    echo "  -r <日主天干>     日主天干，如: 甲、乙、丙... (必填)"
    echo "  -z <四地支>       四柱地支，如: 申巳午寅 (选填)"
    echo "  -g <四天干>       四柱天干，如: 庚辛甲丙 (选填，用于额外分析)"
    echo ""
    echo "示例:"
    echo "  $0 -n 张三 -r 甲 -z 申巳午寅"
    echo "  $0 -n 李四 -r 辛 -z 子丑寅卯"
    echo ""
    echo "输出: 文昌地支、原局有无、是否需要补"
    echo ""
    exit 1
}

# 解析参数
NAME=""
RIZHU=""
ZHIS=""
GANS=""

while getopts "n:r:z:g:" opt; do
    case $opt in
        n) NAME="$OPTARG" ;;
        r) RIZHU="$OPTARG" ;;
        z) ZHIS="$OPTARG" ;;
        g) GANS="$OPTARG" ;;
        *) usage ;;
    esac
done

if [ -z "$NAME" ] || [ -z "$RIZHU" ]; then
    echo "❌ 错误: 姓名和日主天干为必填项"
    usage
fi

echo ""
echo "📋 检查参数: $NAME | 日主: $RIZHU"
if [ -n "$ZHIS" ]; then
    echo "  四柱地支: $ZHIS"
fi
echo ""

# 调用 Python 引擎进行文昌检查
cd "$ENGINE_DIR"

python3 -c "
import sys
sys.path.insert(0, '.')
from shen_sha import get_wen_chang, WEN_CHANG

rizhu = '$RIZHU'
name = '$NAME'
zhi_str = '$ZHIS'
gan_str = '$GANS'

# ── 文昌口诀 ──
print('📜 文昌口诀: 甲巳乙午丙戊申, 丁己酉位庚亥辛, 壬寅癸卯顺推轮')
print('')

# 查文昌对应地支
wc_zhi = get_wen_chang(rizhu)
if not wc_zhi:
    print(f'❌ 未找到日主 {rizhu} 对应的文昌贵人')
    sys.exit(1)

print(f'🔍 日主 {rizhu} → 文昌贵人对应地支: [{wc_zhi}]')
print('')

# 如果传入了四柱地支，检查原局是否有文昌
if zhi_str and len(zhi_str) >= 4:
    zhi_list = list(zhi_str[:4])
    pos_names = ['年支', '月支', '日支', '时支']

    found = False
    found_pos = ''
    for i, z in enumerate(zhi_list):
        if z == wc_zhi:
            found = True
            found_pos = pos_names[i]
            break

    print(f'╔══════════════════════════════════════╗')
    print(f'║  文昌贵人检查结果                     ║')
    print(f'╠══════════════════════════════════════╣')
    print(f'║  姓名: {name}')
    print(f'║  日主: {rizhu}')
    print(f'║  文昌地支: {wc_zhi}')

    if found:
        print(f'║  ✅ 原局有文昌 → 位置: {found_pos}')
        influence = {
            '年支': '祖上书香门第',
            '月支': '少年学业有成',
            '日支': '自身智慧通达',
            '时支': '晚年文昌照拂',
        }
        inf = influence.get(found_pos, '')
        if inf:
            print(f'║  📖 文昌影响: {inf}')
        print(f'║  ✅ 不需要补文昌')
    else:
        print(f'║  ❌ 原局无文昌')
        print(f'║  ⚠️  需要考虑补文昌')
        print(f'║  💡 建议: 佩戴/摆放对应文昌位物品')
        # 给出补文昌具体建议
        wc_supplement = {
            '巳': '东南方，宜摆放文昌塔或毛笔',
            '午': '正南方，宜红色物品或木制文昌塔',
            '申': '西南方，宜金属文昌塔或铜钱',
            '酉': '正西方，宜金属文昌塔或水晶',
            '亥': '西北方，宜黑色/蓝色文昌用品',
            '子': '正北方，宜黑色/蓝色水晶或文昌塔',
            '寅': '东北方，宜绿色文昌竹或木制文昌塔',
            '卯': '正东方，宜绿色植物或木质文昌塔',
        }
        sup = wc_supplement.get(wc_zhi, '宜请文昌塔或求文昌符')
        print(f'║  🏮 建议方位: {sup}')

    print(f'╚══════════════════════════════════════╝')
else:
    print(f'需传入四柱地支 (-z) 才能检查原局是否有文昌')
    print(f'如: $0 -n {name} -r {rizhu} -z <4个地支字符>')

# 额外信息：文昌贵人对应表
print('')
print('📖 文昌贵人对照表:')
for gan, zhi in sorted(WEN_CHANG.items(), key=lambda x: '甲乙丙丁戊己庚辛壬癸'.index(x[0])):
    marker = ' ← 日主' if gan == rizhu else ''
    print(f'   {gan} → {zhi}{marker}')
" 2>&1
