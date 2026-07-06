#!/bin/bash
# 金鉴真人·八字强制验证门禁 v1.0
# 用法: bash bazi-must-verify.sh <年> <月> <日> <时> <分> <性别0/1> <姓名>
# 
# 功能：三步合一，不通过就不输出八字
#   第1步：bazi-engine.py 排盘
#   第2步：bazi-zydx-verify.sh 官网验证
#   第3步：对比一致才输出
#
# 2026-06-23 凤八字错误教训：手动算日柱庚戌❌，引擎官网一致己酉✅
# 从此禁止手动算八字，必须跑此门禁

set -e

YEAR=$1
MONTH=$2
DAY=$3
HOUR=$4
MIN=$5
SEX=$6
NAME=$7

if [ -z "$YEAR" ] || [ -z "$NAME" ]; then
    echo "用法: bash bazi-must-verify.sh <年> <月> <日> <时> <分> <性别0/1> <姓名>"
    exit 1
fi

GENDER="男"
if [ "$SEX" = "0" ] || [ "$SEX" = "女" ]; then
    GENDER="女"
fi

echo "══════════════════════════════════════════"
echo "  八字强制验证门禁 v1.0"
echo "  命主: $NAME | $YEAR年${MONTH}月${DAY}日 ${HOUR}:${MIN} | $GENDER"
echo "══════════════════════════════════════════"

# ===== 自动计算时辰索引 =====
# 子0(23-1) 丑1(1-3) 寅2(3-5) 卯3(5-7) 辰4(7-9) 巳5(9-11)
# 午6(11-13) 未7(13-15) 申8(15-17) 酉9(17-19) 戌10(19-21) 亥11(21-23)
if [ "$HOUR" -ge 23 ] || [ "$HOUR" -lt 1 ]; then SHICHEN=0
elif [ "$HOUR" -ge 1 ] && [ "$HOUR" -lt 3 ]; then SHICHEN=1
elif [ "$HOUR" -ge 3 ] && [ "$HOUR" -lt 5 ]; then SHICHEN=2
elif [ "$HOUR" -ge 5 ] && [ "$HOUR" -lt 7 ]; then SHICHEN=3
elif [ "$HOUR" -ge 7 ] && [ "$HOUR" -lt 9 ]; then SHICHEN=4
elif [ "$HOUR" -ge 9 ] && [ "$HOUR" -lt 11 ]; then SHICHEN=5
elif [ "$HOUR" -ge 11 ] && [ "$HOUR" -lt 13 ]; then SHICHEN=6
elif [ "$HOUR" -ge 13 ] && [ "$HOUR" -lt 15 ]; then SHICHEN=7
elif [ "$HOUR" -ge 15 ] && [ "$HOUR" -lt 17 ]; then SHICHEN=8
elif [ "$HOUR" -ge 17 ] && [ "$HOUR" -lt 19 ]; then SHICHEN=9
elif [ "$HOUR" -ge 19 ] && [ "$HOUR" -lt 21 ]; then SHICHEN=10
else SHICHEN=11
fi
echo "  时辰：${HOUR}:${MIN} → 索引$SHICHEN"

# ===== 第1步：引擎排盘 =====
echo ""
echo "▶ 第1步：引擎排盘..."
ENGINE_OUT=$(python3 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-engine.py --json "$YEAR" "$MONTH" "$DAY" "$HOUR" "$MIN" $SHICHEN "$GENDER" "$NAME" 2>/dev/null) || {
    echo "❌ 引擎排盘失败"
    exit 1
}

# 从JSON中提取八字
ENGINE_BAZI=$(echo "$ENGINE_OUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
pillars = d.get('四柱', {})
print(f\"{pillars.get('年柱','?')} {pillars.get('月柱','?')} {pillars.get('日柱','?')} {pillars.get('时柱','?')}\")
" 2>/dev/null) || ENGINE_BAZI="提取失败"

ENGINE_RIZHU=$(echo "$ENGINE_OUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('日主', '?'))
" 2>/dev/null) || ENGINE_RIZHU="?"

echo "  引擎输出：$ENGINE_BAZI （日主$ENGINE_RIZHU）"

if [ "$ENGINE_BAZI" = "提取失败" ] || [ "$ENGINE_BAZI" = "? ? ? ?" ]; then
    echo "❌ 引擎输出异常，无法提取八字"
    exit 1
fi

# ===== 第2步：官网验证 =====
echo ""
echo "▶ 第2步：官网验证..."
VERIFY_OUT=$(bash /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-zydx-verify.sh "$YEAR" "$MONTH" "$DAY" "$HOUR" "$MIN" "$NAME" "$SEX" 2>/dev/null)

# 从官网输出中提取八字（格式：完整八字: 戊午 甲子 己酉 乙亥）
VERIFY_BAZI=$(echo "$VERIFY_OUT" | grep "完整八字:" | head -1 | sed 's/.*完整八字: //')

if [ -z "$VERIFY_BAZI" ]; then
    echo "❌ 官网验证失败，无法获取八字"
    echo "  原始输出：$VERIFY_OUT"
    exit 1
fi
echo "  官网输出：$VERIFY_BAZI"

# ===== 第3步：对比确认 =====
echo ""
echo "▶ 第3步：对比确认..."
echo "  引擎八字：$ENGINE_BAZI"
echo "  官网八字：$VERIFY_BAZI"

if [ "$ENGINE_BAZI" = "$VERIFY_BAZI" ]; then
    echo ""
    echo "  ✅ 完全一致！验证通过"
    echo ""
    echo "══════════════════════════════════════════"
    echo "  八字：$ENGINE_BAZI"
    echo "  日主：$ENGINE_RIZHU"
    echo "  来源：引擎+官网双验证通过"
    echo "══════════════════════════════════════════"
    echo ""
    echo "$ENGINE_OUT" | python3 -m json.tool 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'【身强弱】{d.get(\"身强弱\",{}).get(\"总分\",\"?\")}分 {d.get(\"身强弱\",{}).get(\"等级\",\"?\")}')
dy = d.get('大运',{})
print(f'【起运】{dy.get(\"起运\",\"?\")}')
for y in dy.get('序列',[]):
    print(f'  {y.get(\"干支\",\"?\")}运 {y.get(\"起始年龄\",\"?\")}~{y.get(\"终止年龄\",\"?\")}岁')
" 2>/dev/null
else
    echo ""
    echo "  ❌ 不一致！引擎=$ENGINE_BAZI vs 官网=$VERIFY_BAZI"
    echo "  停止！检查原因后再试"
    exit 1
fi

# ===== 第4步：输出标准§1骨架（格式锁死，填空即可）=====
echo ""
echo "▶ 第4步：输出标准§1骨架..."
echo "  ✅ 以下直接生成标准§1 25字段格式，填空即可，无需自创格式"
echo ""

# 从JSON提取更多数据
ENGINE_NAYIN=$(echo "$ENGINE_OUT" | python3 -c '
import sys, json; d=json.load(sys.stdin)
n = d.get("\u7eb3\u97f3", {})
print(n.get("\u5e74\u67f1","?") + " / " + n.get("\u6708\u67f1","?") + " / " + n.get("\u65e5\u67f1","?") + " / " + n.get("\u65f6\u67f1","?"))
' 2>/dev/null)

ENGINE_SCORE=$(echo "$ENGINE_OUT" | python3 -c '
import sys, json; d=json.load(sys.stdin)
s = d.get("\u8eab\u5f3a\u5f31", {})
print(str(s.get("\u603b\u5206","?")) + "\u5206 " + s.get("\u7b49\u7ea7","?"))
' 2>/dev/null)

ENGINE_DAYUN=$(echo "$ENGINE_OUT" | python3 -c '
import sys, json; d=json.load(sys.stdin)
dy = d.get("\u5927\u8fd0", {})
print("\u8d77\u8fd0:" + dy.get("\u8d77\u8fd0","?"))
for y in dy.get("\u5e8f\u5217",[])[:5]:
    print(y.get("\u5e72\u652f","?") + " " + str(y.get("\u8d77\u59cb\u5e74\u9f84","?")) + "~" + str(y.get("\u7ec8\u6b62\u5e74\u9f84","?")) + "\u5c81")
' 2>/dev/null)

echo ""
echo "══════════════════════════════════════════"
echo "  【标准§1骨架 — 直接填空，禁止改格式】"
echo "══════════════════════════════════════════"
echo ""
echo "# $NAME·完整八字命理深析报告 v1.0（标准格式·引擎数据校准版）"
echo ""
echo "**编制人：** 金鉴真人"
echo "**编制时间：** $(date '+%Y年%m月%d日')"
echo "**版本：** v1.0（标准格式·引擎数据校准版）"
echo "**模板：** bazi-report-template v5.0（21§标准结构）"
echo "**八字：** $ENGINE_BAZI"
# 根据日主输出五行
RIZHU_WUXING_CASE=$(echo "$ENGINE_RIZHU" | sed 's/[0-9]//g')
case "$RIZHU_WUXING_CASE" in
  甲|乙) RZ_WX="木"; RZ_TYPE="阳木·参天大树"; [ "$RIZHU_WUXING_CASE" = "乙" ] && RZ_TYPE="阴木·花草之木" ;;
  丙|丁) RZ_WX="火"; RZ_TYPE="阳火·太阳之火"; [ "$RIZHU_WUXING_CASE" = "丁" ] && RZ_TYPE="阴火·灯烛之火" ;;
  戊|己) RZ_WX="土"; RZ_TYPE="阳土·城墙之土"; [ "$RIZHU_WUXING_CASE" = "己" ] && RZ_TYPE="阴土·田园之土" ;;
   庚|辛) RZ_WX="金"; RZ_TYPE="阳金·刀剑之金"; [ "$(echo "$ENGINE_RIZHU" | tr -d '0-9')" = "辛" ] && RZ_TYPE="阴金·珠宝之金" ;;
  壬|癸) RZ_WX="水"; RZ_TYPE="阳水·江河之水"; [ "$RIZHU_WUXING_CASE" = "癸" ] && RZ_TYPE="阴水·雨露之水" ;;
  *) RZ_WX="?"; RZ_TYPE="?" ;;
esac
echo "**日主：** ${ENGINE_RIZHU}${RZ_WX}（${RZ_TYPE}）"
# 根据性别输出
PEIOU="正官/七杀"; [ "$GENDER" = "男" ] && PEIOU="正财/偏财"
PAIPAI="阳顺阴逆"; 
# 起运方向由年干阴阳决定（非日主）
Y_GAN=$(echo "$ENGINE_BAZI" | awk '{print substr($1,1,1)}')
YIN_YANG=$(echo "$Y_GAN" | grep -q '[乙丁己辛癸]' && echo "阴" || echo "阳")
if [ "$YIN_YANG" = "阳" ] && [ "$GENDER" = "男" ]; then PAIXIANG="阳男顺排"
elif [ "$YIN_YANG" = "阴" ] && [ "$GENDER" = "女" ]; then PAIXIANG="阴女顺排"
elif [ "$YIN_YANG" = "阴" ] && [ "$GENDER" = "男" ]; then PAIXIANG="阴男逆排"
else PAIXIANG="阳女逆排"
fi
echo "**性别：** $GENDER（$PAIXIANG·配偶星=$PEIOU）"
echo "**出生：** 公历$YEAR-$MONTH-$DAY $HOUR:00（农历待校准）"
echo "**八字来源：** 引擎+官网双验证通过 ✅"
echo ""
echo "---"
echo ""
echo "## §1 一页总览表（25字段·四段式排序）"
echo ""
echo "| 序号 | 项目 | 内容 |"
echo "|:----:|------|------|"
echo "| 1 | **四柱八字** | $ENGINE_BAZI |"
echo "| 2 | **纳音** | $ENGINE_NAYIN |"
echo "| 3 | **日主** | ${ENGINE_RIZHU}${RZ_WX}（${RZ_TYPE}） |"
echo "| 4 | **性别** | $GENDER（$PAIXIANG·配偶星=$PEIOU） |"
echo "| 5 | **出生时间** | 公历${YEAR}-${MONTH}-${DAY} ${HOUR}:00（农历待校准） |"
echo "| 6 | **命格等级** | ⭐⭐⭐ {待填} |"
echo "| 7 | **格局成立条件** | {待填} |"
echo "| 8 | **身强身弱** | $ENGINE_SCORE |"
echo "| 9 | **从弱格排查** | {待填} |"
echo "| 10 | **喜用神（排序）** | 🟢 {待填} |"
echo "| 11 | **忌神（排序）** | 🔴 {待填} |"
echo "| 12 | **空亡** | {待填} |"
echo "| 13 | **财星分数** | {待填}分 |"
echo "| 14 | **财富等级** | 💰 {待填} |"
echo "| 15 | **最高学历** | 🎓 {待填} |"
echo "| 16 | **事业等级** | 🏢 {待填} |"
echo "| 17 | **最佳大运** | 🏆 {待填} |"
echo "| 18 | **起运年龄** | {待填} |"
echo "| 19 | **次佳大运** | 🥇 {待填} |"
echo "| 20 | **最差大运** | ⚠️ {待填} |"
echo "| 21 | **现行大运** | {待填} |"
echo "| 22 | **发财最佳年份** | 🤑 {待填} |"
echo "| 23 | **健康注意方面** | {待填} |"
echo "| 24 | **四大特征** | {待填} |"
echo "| 25 | **搬迁次数预测** | 🚚 {待填} |"
echo ""
echo "> **🗣️ 白话：** {待填}"
echo ""
echo "---"
echo "**验证命令：** bash bazi-must-verify.sh $YEAR $MONTH $DAY $HOUR $MIN $SEX $NAME"
echo ""
echo "【大运数据】"
echo "$ENGINE_DAYUN"
echo ""
echo "══════════════════════════════════════════"
echo "  ⚠️ 禁止自创格式！格式已锁死，直接填空"
echo "  ⚠️ {待填}处填入内容，不要改表结构"
echo "══════════════════════════════════════════"
