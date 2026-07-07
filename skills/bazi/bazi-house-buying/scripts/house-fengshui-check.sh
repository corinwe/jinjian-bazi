#!/bin/bash
# ═════════════════════════════════════════════════════════
# 金鉴真人·买房选房风水检查清单 v1.0
# ═════════════════════════════════════════════════════════
# 用法：bash house-fengshui-check.sh
# 功能：交互式检查买房选房的全部风水要点
# 输出：通过 ✅ / 不通过 ❌ / 需化解 ⚠️ 三色报告
# ═════════════════════════════════════════════════════════

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
PASS=0; FAIL=0; WARN=0; TOTAL=0

report() {
    TOTAL=$((TOTAL+1))
    if [ "$2" == "pass" ]; then PASS=$((PASS+1)); printf "  [${GREEN}✅ 通过${NC}] %s\n" "$1"
    elif [ "$2" == "fail" ]; then FAIL=$((FAIL+1)); printf "  [${RED}❌ 不通过${NC}] %s\n" "$1"
    else WARN=$((WARN+1)); printf "  [${YELLOW}⚠️  需化解${NC}] %s\n" "$1"; fi
}

echo ""; echo "╔══ 金鉴真人·买房选房风水检查清单 ══╗"; echo ""

# ════ 第1部分：选房前准备 ════
echo "━━━ 第1部分：选房前准备 ━━━"
read -p "① 预算是否在承受范围内？(y/n): " ans; [ "$ans" == "y" ] && report "预算在承受范围内" pass || report "预算超支，请重新评估" fail
read -p "② 周边3公里内是否有医院？(y/n): " ans; [ "$ans" == "y" ] && report "3公里内有医院 ✅ 急救有保障" pass || report "附近无医院 ⚠️" warn
read -p "③ 周边是否有超市/菜市场/药店？(y/n): " ans; [ "$ans" == "y" ] && report "生活配套齐全" pass || report "生活配套不足 ⚠️" warn
read -p "④ 是否现房（非期房）？(y/n): " ans; [ "$ans" == "y" ] && report "现房 ✅ 无烂尾风险" pass || report "期房 ⚠️ 注意烂尾风险" warn
read -p "⑤ 物业口碑如何？(好/一般/差): " ans; [ "$ans" == "好" ] && report "物业口碑好" pass; [ "$ans" == "一般" ] && report "物业一般 ⚠️" warn; [ "$ans" == "差" ] && report "物业差 ❌" fail
read -p "⑥ 停车位配比是否充足？(y/n): " ans; [ "$ans" == "y" ] && report "停车位充足" pass || report "停车位不足 ⚠️" warn

# ════ 第2部分：小区四大核心原则 ════
echo ""; echo "━━━ 第2部分：小区四大核心原则（缺一不可）━━━"
read -p "⑦ 小区前面是否有水/路环抱？(y/n): " ans; [ "$ans" == "y" ] && report "有环抱 ✅ 藏风聚气" pass || report "无环抱 ❌ 气散不聚" fail
read -p "⑧ 坐山方向是否有高大建筑/山做靠山？(y/n): " ans; [ "$ans" == "y" ] && report "坐山有靠 ✅ 有贵人" pass || report "坐山无靠 ❌ 第一大忌" fail
read -p "⑨ 关鬼位（克坐山的方位）是否有高大建筑？(y/n，无=通过): " ans; [ "$ans" == "n" ] && report "关鬼位无高大建筑 ✅" pass || report "关鬼位有高大建筑 ❌ 压力大/官司" fail
read -p "⑩ 财/印/食神位是否有高大建筑（有用神）？(y/n): " ans; [ "$ans" == "y" ] && report "有用神 ✅" pass || report "无财印食神位 ❌ 缺用神" fail

# ════ 第3部分：选址十要诀 ════
echo ""; echo "━━━ 第3部分：选址十要诀 ━━━"
read -p "⑪ 小区形状是否方正？(y/n): " ans; [ "$ans" == "y" ] && report "小区方正 ✅" pass || report "小区异形 ⚠️ 四大皆空风险" warn
read -p "⑫ 是否为小区四个角（辰戌丑未位）？(y/n): " ans; [ "$ans" == "n" ] && report "非四角房 ✅" pass || report "四角房 ⚠️ 易破损" warn
read -p "⑬ 是否临街/最前排？(y/n): " ans; [ "$ans" == "n" ] && report "不临街 ✅" pass || report "临街 ❌ 噪音/污染/易失窃" fail
read -p "⑭ 是否小区中间位置？(y/n): " ans; [ "$ans" == "y" ] && report "中间位置 ✅ 最贵但最好" pass || report "非中间位置" warn
read -p "⑮ 是否坐北朝南（子山午向）？(y/n): " ans; [ "$ans" == "y" ] && report "子山午向 ✅ 最佳朝向" pass || report "非坐北朝南 ⚠️" warn
read -p "⑯ 楼间距是否充足？(y/n): " ans; [ "$ans" == "y" ] && report "楼间距充足 ✅" pass || report "楼间距不足 ❌ 采光差" fail

# ════ 第4部分：选单元楼 ════
echo ""; echo "━━━ 第4部分：选单元楼 ━━━"
read -p "⑰ 是否为中间户型（非边户）？(y/n): " ans; [ "$ans" == "y" ] && report "中间户型 ✅ 有左右护" pass || report "边户 ⚠️ 三面悬空" warn
read -p "⑱ 楼栋背后是否有靠山？(y/n): " ans; [ "$ans" == "y" ] && report "楼后有靠 ✅" pass || report "楼后无靠 ⚠️" warn
read -p "⑲ 楼前面是否平阔？(y/n): " ans; [ "$ans" == "y" ] && report "楼前平阔 ✅" pass || report "楼前遮挡 ⚠️" warn

# ════ 第5部分：选楼层 ════
echo ""; echo "━━━ 第5部分：选楼层 ━━━"
read -p "⑳ 是否一楼或顶层？(y/n): " ans; [ "$ans" == "n" ] && report "非天地层 ✅" pass || report "天地层 ⚠️ 一楼湿/顶层风大" warn
read -p "㉑ 楼层尾数(如3楼尾数=3): " floor
read -p "㉒ 门朝向(南/北/东/西/东南/西南/东北/西北): " door
echo "  （请参考bazi-remission-methods §12.4楼层五行表核对）"
report "楼层五行检查（需手动核对）" warn
read -p "㉓ 家人生肖是否与门向无冲？(y/n): " ans; [ "$ans" == "y" ] && report "门向与生肖无冲 ✅" pass || report "门向与生肖相冲 ❌" fail

# ════ 第6部分：户型内部 ════
echo ""; echo "━━━ 第6部分：户型内部风水 ━━━"
read -p "㉔ 户型是否方正？(y/n): " ans; [ "$ans" == "y" ] && report "户型方正 ✅" pass || report "户型不方正 ⚠️ 种流房/缺角" warn
read -p "㉕ 中宫是否为客厅？(y/n): " ans; [ "$ans" == "y" ] && report "中宫为客厅 ✅ 最佳" pass || report "中宫非客厅 ⚠️" warn
read -p "㉖ 是否有火烧天门（厨房在西北）？(y/n): " ans; [ "$ans" == "n" ] && report "无火烧天门 ✅" pass || report "火烧天门 ⚠️ 必须土通关化解" fail
read -p "㉗ 卧室是否避开鬼门线？(y/n): " ans; [ "$ans" == "y" ] && report "卧室不在鬼门线 ✅" pass || report "卧室在鬼门线 ⚠️ 需五岳真形图" warn
read -p "㉘ 主卧门是否不对床？(y/n): " ans; [ "$ans" == "y" ] && report "门不对床 ✅" pass || report "门对床 ⚠️ 需移床或挂门帘" warn
read -p "㉙ 床是否不在横梁下？(y/n): " ans; [ "$ans" == "y" ] && report "无横梁压顶 ✅" pass || report "横梁压顶 ⚠️ 需吊顶" warn
read -p "㉚ 外部是否有煞（路冲/反弓/天斩/尖角）？(y/n): " ans; [ "$ans" == "n" ] && report "外部无煞 ✅" pass || report "外部有煞 ⚠️ 需化解" warn

# ════ 总结 ════
echo ""; echo "═══ 检查总结 ═══"
printf "  ✅ 通过: %d项\n" $PASS; printf "  ❌ 不通过: %d项\n" $FAIL; printf "  ⚠️  需化解: %d项\n" $WARN; printf "  📋 总计: %d项\n" $TOTAL
if [ $FAIL -eq 0 ] && [ $PASS -ge 20 ]; then echo "  🟢 结论：该房子风水条件优秀，可以考虑购买！"
elif [ $FAIL -le 2 ] && [ $WARN -le 5 ]; then echo "  🟡 结论：存在可化解问题，建议用house-remediation-guide.py"
else echo "  🔴 结论：问题较多，建议谨慎考虑或另选！"; fi
echo ""
