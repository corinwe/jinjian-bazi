# 已部署的物理拦截hooks配置（2026-07-16）

## Hooks目录位置（全局共享）
```
/root/.hermes/hooks/bazi-mandatory/
├── precheck.py        # pre_tool_call 物理拦截核心脚本
├── precheck.sh        # shell hook wrapper（调用precheck.py）
├── check.sh           # post_tool_call 审计日志 + 调用verify-format.py
├── inject-context.sh  # pre_llm_call 提醒注入
├── verify-format.py   # 被check.sh调用 → 九龙道长版报告§格式校验（observer-only）
├── verify-energy.py   # 被check.sh调用 → 能量表漏项检查（observer-only）
└── setup-hermes-enterprise.sh  # 六六一键配置脚本
```

## 报告格式校验（verify-format.py — 2026-07-16新增）
- 写报告后自动检查§顺序是否符合bazi-report-template标准
- 九龙道长版：检查§1-§21标题是否匹配模板（§1八字排盘→§21总结）
- 泉师兄盲派版：检查是否包含盲派核心概念（阴阳/五行/体用/格局/做功）
- ⚠️ observer-only，不阻断，仅记录日志到 `~/.hermes/logs/verify/format_warnings.log`

## config.yaml 配置
```yaml
hooks:
  pre_tool_call:
    - /root/.hermes/hooks/bazi-mandatory/precheck.sh
  post_tool_call:
    - /root/.hermes/hooks/bazi-mandatory/check.sh
  pre_llm_call:
    - /root/.hermes/hooks/bazi-mandatory/inject-context.sh
hooks_auto_accept: true
```

## 拦截规则
- 匹配 `write_file|patch` + 文件名含「报告/分析/report/analysis」
- 检查 `/tmp/.bazi_verified` 是否存在
- 存在 → 删除flag → 放行
- 不存在 → block + 返回"请先跑pillar-verify"

## 📌 关键陷阱（2026-07-16实战）
### 陷阱①：post_tool_call返回值被忽略
不阻断。check.sh里的验证脚本能跑但结果不影响交付，只能记录审计日志。
真正能阻断的只有 pre_tool_call（block return）和 pre_verify（continue return）。

### 陷阱②：子代理写错路径
主母泉师兄版报告写到了 `八字命理/` 而非 `八字命格/`。
根因：context中基路径写错了。子代理不会验证父路径是否存在。
解法：每次delegate_task后，ls确认目标父路径+子路径正确。

## 正确交付流程
```bash
# 1. 跑验证
bash projects/bazi-platform/scripts/pillar-verify.py

# 2. 设放行标记
touch /tmp/.bazi_verified

# 3. 写文件（hook自动检测放行）
```

## 六六新Agent配置
```bash
bash /root/.hermes/hooks/bazi-mandatory/setup-hermes-enterprise.sh <profile_name>
```
