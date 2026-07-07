#!/bin/bash
# 生成实时系统状态 JSON

TIMESTAMP=$(date -Iseconds)

# 检查产品页面
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://43.162.90.39:5173)
if [ "$HTTP_CODE" = "200" ]; then
    PAGE_OK="true"
    PAGE_STATUS="HTTP 200"
else
    PAGE_OK="false"
    PAGE_STATUS="HTTP $HTTP_CODE"
fi

# 检查 Python 服务
if ps aux | grep "python.*5173" | grep -v grep > /dev/null; then
    PROCESS_OK="true"
    PROCESS_STATUS="运行中"
else
    PROCESS_OK="false"
    PROCESS_STATUS="未运行"
fi

# 检查 cron 任务
CRONTAB=$(crontab -l 2>/dev/null)

if echo "$CRONTAB" | grep -q "cron-daily-report"; then
    DAILY_OK="true"
    DAILY_STATUS="已配置 (08:00)"
else
    DAILY_OK="false"
    DAILY_STATUS="未配置"
fi

if echo "$CRONTAB" | grep -q "update-data.sh"; then
    UPDATE_OK="true"
    UPDATE_STATUS="已配置 (12:00, 20:00)"
else
    UPDATE_OK="false"
    UPDATE_STATUS="未配置"
fi

if echo "$CRONTAB" | grep -q "cron-hourly-verify"; then
    HOURLY_OK="true"
    HOURLY_STATUS="已配置 (整点)"
else
    HOURLY_OK="false"
    HOURLY_STATUS="未配置"
fi

cat > /var/www/offerpath/system-status.json << EOF
{
  "timestamp": "$TIMESTAMP",
  "checks": [
    {
      "name": "产品页面访问",
      "ok": $PAGE_OK,
      "status": "$PAGE_STATUS"
    },
    {
      "name": "Python 服务进程",
      "ok": $PROCESS_OK,
      "status": "$PROCESS_STATUS"
    },
    {
      "name": "每日汇报任务",
      "ok": $DAILY_OK,
      "status": "$DAILY_STATUS"
    },
    {
      "name": "数据更新任务",
      "ok": $UPDATE_OK,
      "status": "$UPDATE_STATUS"
    },
    {
      "name": "每小时验证",
      "ok": $HOURLY_OK,
      "status": "$HOURLY_STATUS"
    }
  ]
}
EOF

echo "状态已更新：$TIMESTAMP"
