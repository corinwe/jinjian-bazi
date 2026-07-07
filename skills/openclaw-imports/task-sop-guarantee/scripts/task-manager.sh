#!/bin/bash
# 任务执行管理器 - 强制 SOP 流程
# 用法：./task-manager.sh create "任务名称" "任务描述"
#       ./task-manager.sh verify "任务 ID"
#       ./task-manager.sh complete "任务 ID"

WORKSPACE="/root/.openclaw/workspace"
TASK_DB="$WORKSPACE/task-database.json"
TASK_LOG="$WORKSPACE/task-execution.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 初始化数据库
init_db() {
    if [ ! -f "$TASK_DB" ]; then
        cat > "$TASK_DB" << 'EOF'
{
  "version": 1,
  "created_at": "2026-03-23",
  "tasks": [],
  "completed": [],
  "failed": []
}
EOF
    echo "[$TIMESTAMP] 任务数据库已初始化" >> "$TASK_LOG"
fi

# 创建任务
create_task() {
    local name="$1"
    local desc="$2"
    local task_id="TASK-$(date +%s)"
    
    echo "🦐 创建任务：$name"
    echo "   ID: $task_id"
    echo "   时间：$TIMESTAMP"
    echo ""
    
    # 记录到日志
    echo "[$TIMESTAMP] CREATE $task_id: $name - $desc" >> "$TASK_LOG"
    
    # 返回任务 ID
    echo "$task_id"
}

# 验证任务（SOP 核心）
verify_task() {
    local task_id="$1"
    local verify_type="$2"  # http, process, file, content
    
    echo "🔍 验证任务：$task_id"
    echo "   类型：$verify_type"
    echo "   时间：$TIMESTAMP"
    
    local result="PASS"
    
    case $verify_type in
        "http")
            local url="$3"
            local code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
            if [ "$code" = "200" ]; then
                echo "   ✅ HTTP 状态：$code"
            else
                echo "   ❌ HTTP 状态：$code"
                result="FAIL"
            fi
            ;;
        "process")
            local pattern="$3"
            if ps aux | grep "$pattern" | grep -v grep > /dev/null; then
                echo "   ✅ 进程运行中：$pattern"
            else
                echo "   ❌ 进程未运行：$pattern"
                result="FAIL"
            fi
            ;;
        "file")
            local path="$3"
            if [ -f "$path" ]; then
                echo "   ✅ 文件存在：$path"
            else
                echo "   ❌ 文件不存在：$path"
                result="FAIL"
            fi
            ;;
        "content")
            local url="$3"
            local keyword="$4"
            if curl -s "$url" | grep -q "$keyword"; then
                echo "   ✅ 内容验证通过：$keyword"
            else
                echo "   ❌ 内容验证失败：$keyword"
                result="FAIL"
            fi
            ;;
    esac
    
    echo "[$TIMESTAMP] VERIFY $task_id: $result" >> "$TASK_LOG"
    echo "   结果：$result"
    
    [ "$result" = "PASS" ]
}

# 完成任务（必须通过验证）
complete_task() {
    local task_id="$1"
    local verify_result="$2"
    
    if [ "$verify_result" = "PASS" ]; then
        echo "✅ 任务完成：$task_id"
        echo "[$TIMESTAMP] COMPLETE $task_id: SUCCESS" >> "$TASK_LOG"
    else
        echo "❌ 任务失败：$task_id - 验证未通过，不能标记完成"
        echo "[$TIMESTAMP] FAIL $task_id: VERIFICATION_FAILED" >> "$TASK_LOG"
        exit 1
    fi
}

# 列出所有任务
list_tasks() {
    echo "📋 任务列表"
    echo "=========="
    cat "$TASK_LOG" | grep -E "CREATE|VERIFY|COMPLETE|FAIL" | tail -20
}

# 主程序
case "$1" in
    "create")
        init_db
        create_task "$2" "$3"
        ;;
    "verify")
        verify_task "$2" "$3" "$4" "$5"
        ;;
    "complete")
        complete_task "$2" "$3"
        ;;
    "list")
        list_tasks
        ;;
    *)
        echo "用法：$0 {create|verify|complete|list}"
        exit 1
        ;;
esac
