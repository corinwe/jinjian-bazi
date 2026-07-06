#!/bin/bash
# 九龙道长官网八字验证脚本 v2.0
# 用法: bash bazi-zydx-verify.sh <year> <month> <day> <hour> <minute> <name> [sex]
# 基于Python解析HTML，正确提取四柱八字、大运、起运年龄

YEAR=${1:-1980}
MONTH=${2:-8}
DAY=${3:-6}
HOUR=${4:-6}
MIN=${5:-0}
NAME=${6:-"测试"}
SEX=${7:-1}
GENDER="男"; [ "$SEX" = "0" ] && GENDER="女"

echo "══════════════════════════════════════════"
echo "  九龙道长官网排盘验证 v2.0"
echo "  命主: $NAME | $YEAR年${MONTH}月${DAY}日 ${HOUR}:${MIN} | $GENDER"
echo "══════════════════════════════════════════"

# POST方式提交排盘（无需登录）
curl -s -L "https://www.zydx.top/paipan.php" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Accept: text/html,application/xhtml+xml" \
  -H "Accept-Language: zh-CN,zh;q=0.9" \
  -H "Referer: https://www.zydx.top/paipan.php" \
  -H "Origin: https://www.zydx.top" \
  -c /tmp/zydx_cookies.txt \
  --data "act=ok&name=${NAME}&DateType=0&year=${YEAR}&month=${MONTH}&date=${DAY}&hour=${HOUR}&minute=${MIN}&sex=${SEX}" \
  -o /tmp/zydx_response.html 2>/dev/null

# 用Python解析HTML（更准确）
python3 -c "
import re
with open('/tmp/zydx_response.html') as f:
    html = f.read()

# 四柱八字
tg_match = re.search(r'<tr id=\"tgline\">(.*?)</tr>', html, re.DOTALL)
dz_match = re.search(r'<tr id=\"dzline\">(.*?)</tr>', html, re.DOTALL)

tg_spans, dz_spans = [], []
if tg_match:
    tg_spans = [s for s in re.findall(r'<span class=\"big\"[^>]*>([^<]*)</span>', tg_match.group(1)) if s.strip()]
if dz_match:
    dz_spans = [s for s in re.findall(r'<span class=\"big\"[^>]*>([^<]*)</span>', dz_match.group(1)) if s.strip()]

# 四柱天干地支 = 最后4个非空值
tg_pillars = tg_spans[-4:] if len(tg_spans) >= 4 else ['?']*4
dz_pillars = dz_spans[-4:] if len(dz_spans) >= 4 else ['?']*4
pillars = [f'{t}{d}' for t, d in zip(tg_pillars, dz_pillars)]

print(f'完整八字: {pillars[0]} {pillars[1]} {pillars[2]} {pillars[3]}')
print(f'年柱: {pillars[0]}  月柱: {pillars[1]}  日柱: {pillars[2]}  时柱: {pillars[3]}')

# 地支藏干（small标签）
print()
print('【地支藏干】')
cg_spans = re.findall(r'<span class=\"small\">([^<]+)</span>', html)
# Filter to relevant ones - 劫伤印/枭杀才/伤财/才 patterns
relevant_cg = [s for s in cg_spans if re.search(r'[劫伤印枭杀才食官比]', s)]
# Take the last 4 (年柱/月柱/日柱/时柱)
cg_pillars = relevant_cg[-4:] if len(relevant_cg) >= 4 else relevant_cg
pillar_names = ['年支:', '月支:', '日支:', '时支:']
for i, pn in enumerate(pillar_names):
    if i < len(cg_pillars):
        print(f'  {pn} {cg_pillars[i]}')

# 大运序列
print()
print('【大运序列】')
dayun = re.findall(r'data-year=[\"](\\d+)[\"][^>]*>([^<]+)', html)
for age, gan in dayun:
    print(f'  {gan}: data-year={age} (约{int(age)}~{int(age)+10}岁)')

# 称骨命
print()
print('【称骨命】')
weight_m = re.search(r'称骨重量.*?<td[^>]*>([^<]+)</td>', html, re.DOTALL)
comment_m = re.search(r'称骨评语.*?<td[^>]*>([^<]+)</td>', html, re.DOTALL)
if weight_m:
    print(f'  重量: {weight_m.group(1).strip()}')
if comment_m:
    print(f'  评语: {comment_m.group(1).strip()}')
" 2>&1

echo ""
echo "══════════════════════════════════════════"
echo "  ✅ 验证完成（POST方式·无需登录）"
echo "══════════════════════════════════════════"

rm -f /tmp/zydx_cookies.txt
