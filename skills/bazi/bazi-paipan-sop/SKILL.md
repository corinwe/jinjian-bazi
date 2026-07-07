---
name: bazi-paipan-sop
描述: 金鉴真人·八字排盘标准作业程序（SOP）。封装排盘全流程：技能加载顺序→排盘源头校验→引擎评分→分析报告→发布前校验→归档推库。确保每次排盘物理化加载所有必需技能。
tags: [八字, 排盘, SOP, 金鉴真人, pipeline, 物理化]
related_skills: [bazi-engine-workflow, bazi-foundation-analysis, bazi-report-template, bazi-platform-harness, bazi-task-dispatch, maker-checker-workflow, bazi-auto-verify, bazi-calibration]
---

# 金鉴真人·八字排盘SOP v1.0

> 本SOP是排盘流程的**物理化约束**，执行排盘任务时必须按顺序走完所有Phase。
> 
> **加载方式**：已加入config.yaml → skills → auto_load，每次会话自动加载。
> **替代方案**：`skill_view('bazi-paipan-sop')` 手动加载。
> 
> **核心原则**：每一步必须先加载对应技能（skill_view），再从引擎取数据，最后做人工分析。

---

## 📋 Phase 0 — 系统就绪（自动·无需操作）

| 资源 | 来源 | 内容 |
|:-----|:-----|:------|
| SOUL.md | Hermes自动加载 | 身份+原则+Sub-Agent分工 |
| USER.md | Hermes自动注入 | 老板画像+原则+教训 |
| MEMORY.md | Hermes自动注入 | 持久记忆+路径 |
| HERMES.md | 项目级or链自动加载 | 8条铁律+工作流+技能矩阵 |

**验证：** ⚠️ 每次排盘前先`date`确认服务器时间（时区Asia/Shanghai）

---

## 📋 Phase 1 — 加载排盘必需技能

> **必须按此顺序加载，不可跳过。**

### Step 1.1 — 排盘基础
```bash
skill_view('bazi/bazi-foundation-analysis')   # 排盘基础+身强弱+喜用神规则
```
✅ 确认内容：排盘基础规则、身强弱判定标准、藏干十神表

### Step 1.2 — 引擎工作流
```bash
skill_view('bazi-engine-workflow')             # 大运规则+流年规则+引擎调用方式
# ⚠️ 已auto_load → 但仍需确认以下规则已加载：
#   - 大运年龄ceil向上取整
#   - Q4进位（浮点月份偏移）
#   - 大运天干地支分开判喜忌
#   - 大运前5年天干70%/后5年地支70%
#   - 流年上午天干/下午地支
#   - 大运+流年叠加判断
```

### Step 1.3 — 报告模板
```bash
skill_view('bazi-report-template')             # 21§标准模板+年龄向上取整规则
```
✅ 确认内容：21§模板完整、大运年龄向上取整、能量分阶段规则

### Step 1.4 — 平台架构
```bash
skill_view('bazi-platform-harness', 'references/project-config.md')  # 项目配置+路径
```
✅ 确认内容：项目路径、知识库路径、推库命令

### Step 1.5 — 校验工具
```bash
skill_view('bazi/bazi-auto-verify')            # 自动验证规则
```
✅ 确认内容：验证流程、常见错误模式

---

## 📋 Phase 2 — 排盘 + 源头校验

> **铁律：排盘必须跑引擎，禁止手算。**

### Step 2.1 — 排盘门禁脚本
```bash
bash projects/bazi-platform/scripts/bazi-must-run-engine.sh -n <姓名> -g <性别> -y <年> -m <月> -d <日> -h <时>
```
✅ 这个脚本自动完成：
   - 调用 `paipan.py` 排四柱八字
   - 调用 `canggan-parse.py` 源头校验（标出藏干十神易混淆项）
   - 输出结果到 `/tmp/bazi_output.json`

### Step 2.2 — 人工验证排盘结果
```bash
# 用引擎JSON验证关键数据
python3 -c "
from paipan import paipan
b = paipan('姓名', '性别', 年, 月, 日, 时)
print(f'八字: {b.summary()}')
# 检查是否有易混淆项
"
```
✅ 检查要点：
   - 五鼠遁口诀验证时柱（`skill_view('bazi/bazi-wushidun-verify')`）
   - 月柱节气验证
   - 藏干十神逐一核对

---

## 📋 Phase 3 — 完整引擎评分

> **数据来源：引擎计算，LLM不做计算只做翻译。**

### Step 3.1 — 调用pipeline_v5
```bash
cd projects/bazi-platform/engine/tests && python3 -c "
from pipeline_v5 import run_v5
from paipan import paipan
b = paipan('姓名', '性别', 年, 月, 日, 时)
result = run_v5(b, 年, 月, 日, 节气天数)
# 输出所有§的JSON
import json; print(json.dumps(result, ensure_ascii=False, indent=2))
"
```

### Step 3.2 — 提取关键数据
从引擎JSON提取：
```
data['大运']['序列']           → 大运年份（唯一真值，禁止自行计算）
data['身强弱']['分数']         → 身强弱分数
data['身强弱']['标签']         → 身强弱标签（身强/身弱/从格）
data['财星']['总分']           → 财星评分
data['喜用神']                 → 喜用神列表
data['忌神']                   → 忌神列表
```

---

## 📋 Phase 4 — 分析 + 出报告

### Step 4.1 — 加载对应事象技能
```bash
skill_view('bazi-wealth-analysis')        # 财富
skill_view('bazi-marriage-analysis')      # 婚姻
skill_view('bazi-education-analysis')     # 学业
skill_view('bazi-children-analysis')      # 子女
skill_view('bazi-career-analysis')        # 事业
skill_view('bazi-health-psychology')      # 健康
skill_view('bazi-misfortune-analysis')    # 灾祸
skill_view('bazi-remission-methods')      # 化解
skill_view('bazi-liunian-analysis')       # 流年
skill_view('bazi-birthtime-analysis')     # 时辰判断（如需）
```

### Step 4.2 — 逐§写分析
```bash
skill_view('bazi-report-template')        # 确认模板最新版
```
🚨 **铁律**：
   - 分析文本**亲自写**，不靠自动生成
   - 每行内容必须有**引擎数据 + 技能规则 双支撑**
   - 禁止模板话术/通用占位符
   - 大运年龄按**向上取整(ceil)**显示
   - 大运喜忌按**干支分别判定**

### Step 4.3 — Maker/Checker循环
```bash
skill_view('maker-checker-workflow')
```
1. Maker写分析 → Checker审查
2. Checker发现问题 → Maker修改
3. 循环直到Checkers通过

---

## 📋 Phase 5 — 发布前校验

### Step 5.1 — 五关校验
```bash
python3 projects/bazi-platform/scripts/pillar-verify.py
```
✅ 5关：五鼠遁 → 藏干十神 → 结构优先级 → 全局冲刑 → 最优性

### Step 5.2 — 全量测试
```bash
cd projects/bazi-platform/engine/tests && python3 validate_all.py
```
✅ 320条门禁全部通过

### Step 5.3 — 内容级校验
```bash
skill_view('bazi-calibration')            # 校准体系
```
✅ 对每个输出数值展示三段式证据链：
   - 数据来源（引擎哪个字段）
   - 规则来源（技能哪个规则+行号）
   - 结论

---

## 📋 Phase 6 — 归档 + 推库

### Step 6.1 — 放入人物档案（禁止写入/root/）
```bash
cp <报告文件> /root/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案/<序号>-<姓名>/
```
🚨 **铁律**：所有人物八字分析报告只放知识库人物档案，**禁止写入 `/root/`**。

### Step 6.2 — 推库
```bash
cd /root/weiwuji-knowledge-base
git add -A && git commit -m "📖 <消息>" && git push
cd /root/.hermes/profiles/jinjian-zhenren
git add -A && git commit -m "🧮 <消息>" && git push
```

---

## 🚨 终止条件

每个Phase完成后必须确认下一Phase可以开始：

| Phase | 终止条件 | 验证方式 |
|:------|:---------|:---------|
| 1 | 所有必需技能已skill_view | 检查技能内容不为空 |
| 2 | 排盘JSON输出到/tmp | `test -f /tmp/bazi_output.json` |
| 3 | 引擎21§全量输出 | `jq '. \| keys' /tmp/bazi_output.json` |
| 4 | 报告完整21§ | 目视检查每§存在 |
| 5 | 5关+320门禁全绿 | 查看exit code |
| 6 | git push成功 | 查看commit hash |

---

## 📌 参考文献

| 文件 | 路径 |
|:-----|:------|
| 项目铁律+技能矩阵 | `skill_view('bazi-platform-harness', 'references/project-config.md')` |
| 排盘门禁脚本 | `projects/bazi-platform/scripts/bazi-must-run-engine.sh` |
| 引擎代码 | `projects/bazi-platform/engine/` |
| 知识库 | `/root/weiwuji-knowledge-base` |
