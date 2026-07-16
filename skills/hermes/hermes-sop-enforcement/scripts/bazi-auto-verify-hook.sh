#!/usr/bin/env bash
# post_tool_call hook — 写完文件后自动验证
# 配置方式：在 config.yaml 的 hooks.post_tool_call 中引用此脚本
#
# matcher 匹配 write_file|patch 时触发
# 从 stdin 接收 JSON：{"tool_name":"write_file","arguments":{"path":"...","content":"..."}}
# stdout 返回 JSON：{"inject":"验证结果文本"} 或空（不干预）

INPUT=$(cat /dev/stdin)

# 只验证报告文件（.md 且路径含指定关键字）
FILE_PATH=$(echo "$INPUT" | python3 -c "
import json,sys
try:
    d=json.load(sys.stdin)
    args = d.get('arguments', {})
    path = args.get('path', '') or args.get('file_path', '')
    print(path)
except:
    print('')
" 2>/dev/null)

# 非报告文件不验证
if [[ "$FILE_PATH" != *".md" ]]; then
    exit 0
fi

# 执行验证（如果有验证脚本）
VERIFY_SCRIPT="/root/.hermes/profiles/jinjian-zhenren/scripts/bazi-verify-report.sh"
if [ -f "$VERIFY_SCRIPT" ]; then
    RESULT=$(bash "$VERIFY_SCRIPT" "$FILE_PATH" 2>&1)
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -ne 0 ]; then
        # 验证失败 → 向 LLM 注入错误信息，阻止 Agent 声称完成
        python3 -c "
import json
msg = json.dumps({'inject': '❌ 自动验证失败！报告 '$FILE_PATH' 未通过检查。\\n错误信息：' + '''$RESULT''' + '\\n请修复后再试。'})
print(msg)
"
        exit 0
    fi
fi

# 验证通过 → 不注入任何内容
echo '{}'
