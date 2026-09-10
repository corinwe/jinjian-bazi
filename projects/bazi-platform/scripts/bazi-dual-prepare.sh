#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 金鉴真人 · 双引擎数据源准备（物理体系入口·唯一）
# ═══════════════════════════════════════════════════════════════
# 默认行为：同时生成【八字数据源 + 紫微数据源】并做四柱交叉校验。
# 除非老板明确说明，否则**不允许**只跑单引擎。
#
# 用法：
#   bash scripts/bazi-dual-prepare.sh 姓名 性别 公历YYYY-MM-DD HH:MM [出生地]
#   bash scripts/bazi-dual-prepare.sh 七七 女 2017-07-07 08:00 上海
#
# 豁免模式（仅老板明确要求时使用）：
#   --bazi-only   只用传统八字，不跑紫微   → 创建 /tmp/.bazi_only
#   --ziwei-only  只用紫微，不用传统八字   → 创建 /tmp/.ziwei_only
#   取消豁免：--reset
# ═══════════════════════════════════════════════════════════════
set -o pipefail

PROJ="/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform"
cd "$PROJ" || exit 1

MODE="dual"
ARGS=()
for a in "$@"; do
  case "$a" in
    --bazi-only)  MODE="bazi" ;;
    --ziwei-only) MODE="ziwei" ;;
    --reset)      rm -f /tmp/.bazi_only /tmp/.ziwei_only
                  echo "✅ 已清除豁免标记，恢复【默认双引擎】模式"; exit 0 ;;
    *) ARGS+=("$a") ;;
  esac
done

if [ ${#ARGS[@]} -lt 4 ]; then
  sed -n '1,20p' "$0"
  exit 1
fi

NAME="${ARGS[0]}"; GENDER="${ARGS[1]}"; DATE="${ARGS[2]}"; TIME="${ARGS[3]}"
LOC="${ARGS[4]:-}"

echo "═══════════════════════════════════════════════"
echo " 金鉴真人 · 数据源准备  [$NAME $GENDER $DATE $TIME $LOC]"
echo "═══════════════════════════════════════════════"

case "$MODE" in
  bazi)
    rm -f /tmp/.ziwei_only; touch /tmp/.bazi_only
    echo "⚠️  豁免模式：**只用传统八字**（老板特别指定）"
    echo "    已创建 /tmp/.bazi_only —— 报告将不含紫微内容"
    ;;
  ziwei)
    rm -f /tmp/.bazi_only; touch /tmp/.ziwei_only
    echo "⚠️  豁免模式：**只用紫微斗数**（老板特别指定）"
    echo "    已创建 /tmp/.ziwei_only —— 报告将不含八字内容"
    ;;
  dual)
    rm -f /tmp/.bazi_only /tmp/.ziwei_only
    echo "✅ 默认模式：**八字 × 紫微 双引擎合参**"
    ;;
esac

Y=$(echo "$DATE" | cut -d- -f1); M=$(echo "$DATE" | cut -d- -f2); D=$(echo "$DATE" | cut -d- -f3)
H=$(echo "$TIME" | cut -d: -f1); MI=$(echo "$TIME" | cut -d: -f2)
H=${H#0}; MI=${MI#0}; M=${M#0}; D=${D#0}; H=${H:-0}; MI=${MI:-0}

# ── ① 八字数据源 ──
if [ "$MODE" != "ziwei" ]; then
  echo ""
  echo "── ① 八字引擎 → /tmp/${NAME}_engine.json ──"
  python3 scripts/bazi-engine.py "$Y" "$M" "$D" "$H" "$MI" \
      $(( (H==23||H==0) ? 0 : ((H+1)/2%12) )) "$GENDER" "$NAME" "$LOC" --json \
      > "/tmp/${NAME}_engine.json" 2>/tmp/bazi_err.log || { echo "❌ 八字引擎失败"; tail -5 /tmp/bazi_err.log; exit 1; }
  echo "── ② 八字数据源 → /tmp/${NAME}_ds.json ──"
  python3 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-data-source.py \
      "/tmp/${NAME}_engine.json" "/tmp/${NAME}_ds.json" >/dev/null || { echo "❌ 数据源生成失败"; exit 1; }
  export BAZI_DATASOURCE="/tmp/${NAME}_ds.json"
  echo "   ✅ $(python3 -c "import json;d=json.load(open('/tmp/${NAME}_ds.json'));print('八字:',d.get('八字'),'| 日主:',d.get('日主'),'| 身强弱:',d.get('身强弱',{}).get('等级'))")"
fi

# ── ③ 紫微数据源 ──
if [ "$MODE" != "bazi" ]; then
  echo ""
  echo "── ③ 紫微引擎（第四引擎）→ /tmp/${NAME}_ziwei.json ──"
  python3 engine/ziwei_engine.py "$NAME" "$GENDER" "$DATE" "$TIME" ${LOC:+"$LOC"} \
      >/dev/null 2>/tmp/ziwei_err.log || { echo "❌ 紫微引擎失败"; tail -5 /tmp/ziwei_err.log; exit 1; }
  python3 -c "
import json
d=json.load(open('/tmp/${NAME}_ziwei.json'))
cv=d['四柱交叉校验']; z=d['紫微']
print('   紫微:', cv['紫微引擎'], '| 八字:', cv['八字引擎'], '|', cv['说明'])
print('   五行局:', z['五行局'], '| 命主:', z['命主'], '| 身主:', z['身主'])
"
fi

# ── ④ 交叉校验门禁 ──
if [ "$MODE" = "dual" ]; then
  CONSIST=$(python3 -c "
import json
try:
    d=json.load(open('/tmp/${NAME}_ziwei.json'))
    print('1' if d.get('四柱交叉校验',{}).get('一致') else '0')
except Exception: print('0')
")
  if [ "$CONSIST" != "1" ]; then
    echo ""
    echo "🚨🚨 双引擎四柱不一致 —— 禁止出报告！"
    echo "    先跑: python3 scripts/bazi-jieqi-regression.py --quick"
    echo "    定位 engine/jieqi.py 的节气定界问题，修好再继续。"
    exit 2
  fi
  echo ""
  echo "✅ 双引擎四柱交叉校验通过"
fi

echo ""
echo "═══════════════════════════════════════════════"
echo " 数据源就绪（BAZI_DATASOURCE=${BAZI_DATASOURCE:-未设置}）"
echo " 写报告前请执行: touch /tmp/.bazi_verified"
echo " 模式: $MODE $([ "$MODE" = "dual" ] && echo '（八字+紫微合参）' || echo '（豁免单引擎）')"
echo "═══════════════════════════════════════════════"
