---
name: bazi-platform-harness
description: 八字排盘平台 — 项目架构、路径配置、部署信息
tags: [bazi, platform, config, harness]
related_skills:
  - bazi-paipan-sop
  - bazi-report-template
---

# 八字排盘平台 · 平台架构

> **来源**: 基于项目实际部署路径和配置。用于Phase 1.4加载项目配置信息。

## §1. 项目路径

| 配置项 | 路径 |
|:------|:-----|
| 项目根目录 | `/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform` |
| 引擎模块 | `{project}/engine/` |
| 排盘脚本 | `{project}/scripts/` |
| 后端API | `{project}/api/` |
| 数据库 | `{project}/backend/` |

## §2. 知识库路径

| 配置项 | 路径 |
|:------|:-----|
| 知识库根目录 | `/root/weiwuji-knowledge-base/` |
| 人物档案 | `{kb}/07-国学哲学/八字命格/02-人物档案/` |
| 八字规则 | `{kb}/07-国学哲学/八字命格/01-八字规则理论/` |

## §3. 推库命令

```bash
# 双库推库
cd /root/weiwuji-knowledge-base && git add -A && git commit -m "📖 ..." && git push
cd /root/.hermes/profiles/jinjian-zhenren && git add -A && git commit -m "🧮 ..." && git push
```

## §4. 参考文件

| 文件 | 说明 |
|:-----|:------|
| `references/arkclaw-engineering-patterns-20260716.md` | 🆕 外部工程模式参考：ArkClaw财报分析工具的工程学方法（错误隔离屏障+多入口设计） |
| `references/session-lessons-20260718.md` | 🆕 2026-07-18会话经验：财星检测铁律/三决断原则/丙火巳月特例/文昌公式/佩戴数字/更新下沉规则 |

## §5. 关键注意事项

- **CWD要求**: 所有 `cd projects/bazi-platform/` 命令必须从 `/root/.hermes/profiles/jinjian-zhenren/` 开始执行
- **引擎JSON路径**: `/tmp/{姓名}_engine.json`
- **报告路径**: `/tmp/{姓名}_报告.md`
