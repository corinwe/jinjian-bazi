---
name: bazi-platform-harness
description: 🚨 八字排盘平台·工程化落地总调度Harness。v7.3新增铁律㉑SOUL.md/USER.md文件持久化(2026-07-06 角色+用户画像写入磁盘跨会话可用)+新增references/SOUL.md+references/USER.md。v7.2新增铁律⑲排盘源头藏干十神校验+铁律⑳四柱分析5关校验。v7.1新增铁律⑱(2026-07-05 generate_deep_report空paipan → bazi_string解析固化)。当老板说「开发/设计/写代码/测试/验证/部署/改功能/加模块/修Bug」时强制加载。整合所有工程技能为一条自动化流水线。
category: software-development
tags: [八字, 排盘, 工程化, 校验, 流水线]
---

# 🏗️ 八字排盘平台 · 工程化落地总调度 Harness v7.3

> 金鉴真人的工程化身份：Orchestrator（拆任务+验结果）
> Sub-Agent分工体系、任务派发流程详见 `references/SOUL.md`（本技能附带的身份固化文档）
> 老板画像、原则、风格详见 `references/USER.md`（本技能附带的用户画像文档）

---

## 🔥 物理铁律速查

| 铁律 | 内容 | 来源 |
|:----|:-----|:------|
| ① 排盘门禁 | `bash /root/bazi-platform/scripts/bazi-must-run-engine.sh` | 2026-06-29 |
| ② 知识库路径 | `/root/weiwuji-knowledge-base/...` | 固化 |
| ③ 不依赖记忆 | 所有路径/规则从文件读取 | 固化 |
| ④ 报告格式 | 21§标准，§1 25字段四段式 | bazi-report-template |
| ⑤ 大运校验 | 结束年-开始年+1=10 | 2026-07-01 |
| ⑥ 节气自动计算 | 禁用硬编码qi_yun_days | 2026-07-05 |
| ⑦ int截断检查 | 起运年龄全程浮点数 | 2026-07-05 |
| ⑧ 全量审计流程 | 引擎→脚本→测试→大运→报告 | 2026-07-05 |
| ⑨ generate_deep_report | 用bazi_str解析代替空paipan | 2026-07-05 |
| ⑩ 全链路字段名校验 | generate_deep_report字段名一致性 | 2026-07-05 |
| ⑪ 版本对齐 | engine/backend/api版本号一致 | 2026-07-05 |
| ⑫ 旧版归档 | 归档后须运行引擎抓ImportError | 2026-07-05 |
| **⑲ 排盘源头校验** | **bazi-must-run-engine.sh自动调canggan-parse.py标易混淆⚠️** | **2026-07-06** |
| **⑳ 四柱分析校验** | **pillar-verify.py 5关校验，结论发布前强制跑** | **2026-07-06** |
| **㉑ SOUL/USER持久化** | **SOUL.md+USER.md写入磁盘，跨会话可用。AGENTS.md已引用。备用路径：knowledge-base/04-金鉴真人体系/** | **2026-07-06** |

---

## 📐 验证流水线

| 命令 | 说明 | 时机 |
|:-----|:------|:------|
| `python3 /root/bazi-platform/scripts/canggan-parse.py /tmp/bazi_last_result.json` | 排盘后自动调：藏干十神解析 + 易混淆标注 | 每次排盘后 |
| `python3 /root/bazi-platform/scripts/pillar-verify.py` | 四柱分析前跑：5关校验（五鼠遁/十神/结构/冲刑/最优性） | 分析发布前 |
| `python3 /root/bazi-platform/scripts/verify_report.py` | 报告发布前跑：7项格式校验 | 报告发布前 |
| `cd /root/bazi-platform/engine/tests && python3 validate_all.py` | 引擎全量验证 | 代码修改后 |

---

## 📂 本技能包含的文件

| 文件 | 说明 |
|:-----|:------|
| `references/SOUL.md` | 🔥 金鉴真人身份固化文档：身份+原则+铁律+分工体系（原系统提示，2026-07-06物理化） |
| `references/USER.md` | 🔥 老板用户画像固化文档：谁+原则+风格+6大核心教训（原memory，2026-07-06物理化） |
| `references/engineering-checklists.md` | 工程检查清单 |
| `references/project-config.md` | 项目配置（含验证命令、铁律、测试速查） |
| `references/physical-pipeline-20260706.md` | 物理化流水线 |
| `references/full-chain-verification.md` | 全链路验证 |
| ...（另含19个参考文件，详见linked_files） |

---

## ⚠️ 加载本技能时必须做的

1. `skill_view('bazi-platform-harness', 'references/project-config.md')` → 加载完整配置
2. `skill_view('bazi-platform-harness', 'references/SOUL.md')` → 加载身份设定
3. `skill_view('bazi-platform-harness', 'references/USER.md')` → 加载老板画像
4. 排盘前: 确认`/tmp/bazi_last_result.json`已更新（由bazi-must-run-engine.sh生成）
5. 发布报告前: 跑`verify_report.py`确认格式通过
6. 四柱分析结论发布前: 跑`pillar-verify.py`确认5关全过
