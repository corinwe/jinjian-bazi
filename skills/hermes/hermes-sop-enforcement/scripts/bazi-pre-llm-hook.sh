#!/usr/bin/env bash
# pre_llm_call hook — 每次LLM调用前注入SOP检查提醒
# 配置方式：在 config.yaml 的 hooks.pre_llm_call 中引用此脚本
#
# stdout 返回 JSON: {"inject":"提醒文本"}
# 注入的文本会出现在 LLM 的上下文中

# 检查当前是否有未完成的验证任务
REPORT_DIR="/tmp/bazi_reports"
INCOMPLETE=0

if [ -d "$REPORT_DIR" ]; then
    for f in "$REPORT_DIR"/*.md; do
        [ -f "$f" ] || continue
        # 检查是否有验证标记
        if ! grep -q "✅ 验证通过" "$f" 2>/dev/null; then
            INCOMPLETE=1
            break
        fi
    done
fi

if [ $INCOMPLETE -eq 1 ]; then
    python3 -c "
import json
msg = json.dumps({
    'inject': '⚠️ 注意：当前有待验证的报告尚未通过pillar-verify。在交付前，请确保先运行验证脚本并确认全部通过。'
})
print(msg)
"
    exit 0
fi

# 一切正常 → 不注入
echo '{}'
