# 已部署的物理拦截hooks配置（2026-07-16）

## Hooks目录位置（全局共享）
```
/root/.hermes/hooks/bazi-mandatory/
├── precheck.py        # pre_tool_call 物理拦截核心脚本
├── precheck.sh        # shell hook wrapper（调用precheck.py）
├── check.sh           # post_tool_call 审计日志（observer-only）
├── inject-context.sh  # pre_llm_call 提醒注入
└── setup-hermes-enterprise.sh  # 六六一键配置脚本
```

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
