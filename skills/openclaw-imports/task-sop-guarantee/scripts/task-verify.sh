#!/bin/bash
# 任务验证脚本 - 每次汇报前必须运行

echo "🦐 任务验证报告 - $(date)"
echo "================================"

# 1. 检查产品页面
echo -e "\n1️⃣ 产品页面检查:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://43.162.90.39:5173)
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ HTTP 状态：$HTTP_CODE"
    CONTENT=$(curl -s http://43.162.90.39:5173 | head -100)
    if echo "$CONTENT" | grep -q "Offer 路书\|offerpath\|榜单\|学校\|名校录取"; then
        echo "   ✅ 内容检查：产品页面正常"
    else
        echo "   ❌ 内容检查：页面内容不对！"
        echo "   实际内容预览："
        echo "$CONTENT" | head -20
    fi
else
    echo "   ❌ HTTP 状态：$HTTP_CODE (应该 200)"
fi

# 2. 检查服务进程
echo -e "\n2️⃣ 服务进程检查:"
if ps aux | grep "python.*5173" | grep -v grep > /dev/null; then
    echo "   ✅ Python 服务运行中"
else
    echo "   ❌ Python 服务未运行"
fi

# 3. 检查定时任务
echo -e "\n3️⃣ 定时任务检查:"
if crontab -l 2>/dev/null | grep -q "cron-daily-report"; then
    echo "   ✅ 日报定时任务已配置"
    crontab -l | grep "cron-daily-report"
else
    echo "   ❌ 日报定时任务未配置"
fi

echo -e "\n================================"
echo "验证完成时间：$(date +%s)"
