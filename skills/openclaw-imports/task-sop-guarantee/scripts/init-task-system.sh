#!/bin/bash
# 任务系统初始化脚本

WORKSPACE="/root/.openclaw/workspace"

echo "🦐 初始化任务执行保证系统..."

# 1. 创建任务数据库
cat > "$WORKSPACE/task-database.json" << 'DBEOF'
{
  "version": 1,
  "created_at": "$(date -Iseconds)",
  "tasks": [],
  "completed": [],
  "failed": []
}
DBEOF
echo "✅ 任务数据库已创建：task-database.json"

# 2. 创建执行日志
touch "$WORKSPACE/task-execution.log"
echo "✅ 执行日志已创建：task-execution.log"

# 3. 创建每小时验证脚本
cat > "$WORKSPACE/cron-hourly-verify.sh" << 'CRONEOF'
#!/bin/bash
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
CRONEOF
chmod +x "$WORKSPACE/cron-hourly-verify.sh"
echo "✅ 每小时验证脚本已创建"

# 4. 配置 crontab
if ! crontab -l 2>/dev/null | grep -q "cron-hourly-verify"; then
    (crontab -l 2>/dev/null; echo "0 * * * * $WORKSPACE/cron-hourly-verify.sh") | crontab -
    echo "✅ crontab 已配置（每小时验证）"
else
    echo "⚠️ crontab 已存在，跳过"
fi

# 5. 创建任务追踪表
cat > "$WORKSPACE/task-tracker.md" << 'TRACKEREOF'
# 任务追踪表

| 任务 ID | 任务名称 | 状态 | 创建时间 | 验证状态 |
|---------|---------|------|---------|---------|
| (自动填充) | | | | |
TRACKEREOF
echo "✅ 任务追踪表已创建"

echo ""
echo "🎉 任务系统初始化完成！"
echo ""
echo "使用方法："
echo "  1. 创建任务：./scripts/task-manager.sh create \"任务名\" \"描述\""
echo "  2. 验证任务：./scripts/task-manager.sh verify \"TASK-xxx\" \"http\" \"http://...\""
echo "  3. 完成任务：./scripts/task-manager.sh complete \"TASK-xxx\" \"PASS\""
echo "  4. 查询任务：./scripts/task-manager.sh list"
