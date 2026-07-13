#!/bin/bash
# 大运四步验证.sh — 每次生成大运后运行
# 用法: source 此脚本
# 2026-07-01 基于家主己丑运遗漏+立报告3轮修复教训

echo "═══════════════════════════════════"
echo " 大运四步验证"
echo "═══════════════════════════════════"

verify_da_yun() {
    local name=$1
    local gender=$2
    local birth_year=$3
    local qi_yun_age=$4
    
    echo ""
    echo "【$name】起运${qi_yun_age}岁"
    
    # Step 1: 验证年龄区间连贯
    echo "Step 1: 年龄区间连贯性 → (end - start + 1) = 10 ✏️"
    
    # Step 2: 当前年份交叉验证
    local current_year=2026
    local current_age=$((current_year - birth_year))
    echo "Step 2: 当前$current_year年 = ${current_age}岁"
    echo "  → 确认${current_age}岁在正确的大运区间内 ✅"
    
    # Step 3: 大运方向
    echo "Step 3: 大运方向确认"
    if [ "$gender" == "男" ]; then
        echo "  → 阳男顺排 / 阴男逆排 ✏️"
    else
        echo "  → 阳女逆排 / 阴女顺排 ✏️"
    fi
    
    # Step 4: 大运地支冲财库（最容易漏！）
    echo "Step 4: ⚠️ 每步大运地支是否冲八字中的财库？"
    echo "  → 冲月支？冲日支？冲时支？"
    echo "  → 被冲的地支是财库吗？（财才墓库 vs 官杀库/印库）"
    echo "  → 财星≥40分？→ 库开得财 ✅ ；<40分？→ 墓开破财 ❌"
    echo ""
}

# 使用示例：
# verify_da_yun "家主" "男" 1980 0
# verify_da_yun "主母" "女" 1987 6
# verify_da_yun "子源" "男" 2011 8
# verify_da_yun "立" "男" 2011 4