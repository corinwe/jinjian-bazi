#!/bin/bash
# 每小时自动验证任务执行状态

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/hourly-verify.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 更新系统状态
$WORKSPACE/scripts/update-status.sh >> $LOG_FILE 2>&1

# 运行验证脚本
echo "[$TIMESTAMP] 开始验证..." >> $LOG_FILE
$WORKSPACE/scripts/task-verify.sh >> $LOG_FILE 2>&1

# 如果发现异常，记录告警
if ! curl -s -o /dev/null -w "%{http_code}" http://43.162.90.39:5173 | grep -q "200"; then
    echo "[$TIMESTAMP] ⚠️ 告警：产品页面访问异常" >> $LOG_FILE
fi

if ! ps aux | grep "python.*5173" | grep -v grep > /dev/null; then
    echo "[$TIMESTAMP] ⚠️ 告警：Python 服务未运行" >> $LOG_FILE
fi

echo "[$TIMESTAMP] 验证完成" >> $LOG_FILE
