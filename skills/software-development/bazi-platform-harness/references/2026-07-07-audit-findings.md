# 2026-07-07 全量审计发现与修复记录

## 审计范围
端到端审计：加载链 → HERMES.md → config.yaml → scripts → hooks → skills → git

## 发现的问题

### ① HERMES.md L97：skills路径错误
- **旧**：`projects/bazi-platform/skills/`（路径不存在 ❌）
- **新**：`skills/`（profile根目录 ✅）

### ② check.sh钩子引用2个不存在的脚本
- `bazi-format-check.py` → MISSING（已创建）
- `bazi-report-validator.py` → MISSING（已创建）
- 当前效果：post_tool_call钩子在output_file为空时静默跳过

### ③ skills/曾是破损git子模块
- 旧：skills/是git子模块（mode 160000），子模块未正确初始化
- 修复：`git rm --cached skills/` → `git add skills/` 直接跟踪文件
- 新增 `skills/.gitignore` 排除 Hermes 内部数据

### ④ skill_manage symlink bug workaround
- 现象：skill_manage 无法写入 symlink 指向的技能文件
- 已写入 bazi-platform-harness 技能

## 本次新增资产
| 资产 | 路径 | 作用 |
|:-----|:-----|:-----|
| 排盘SOP技能 | skills/bazi/bazi-paipan-sop/ | 6 Phase流水线，auto_load |
| 格式校验器 | scripts/bazi-format-check.py | 检查21§/大运年龄/配偶特征 |
| 报告验证器 | scripts/bazi-report-validator.py | 内容级验证 |

## 本次固化的规则
| 规则 | 所在技能 | 内容 |
|:-----|:---------|:------|
| 大运年龄向上取整 | da_yun.py + template | ceil(qi_yun_age) |
| 大运天干地支分开判喜忌 | bazi-engine-workflow | 不可笼统说"双忌神" |
| 大运前5年天干70%/后5年70% | bazi-engine-workflow | 能量分阶段 |
| 流年干支分管时间 | bazi-engine-workflow | 上半年天干/下半年地支 |
| 配偶特征只列实际地支 | bazi-report-template | 禁止"寅申巳亥"全组列举 |
| 丙戌大运一喜一忌 | bazi-report-template | 正官是喜用不是忌神 |
| 补开财库+补文昌方案 | bazi-report-template | 通用方案 |
| 老板沟通规范 | bazi-task-dispatch | 沟通风格+核心原则 |
