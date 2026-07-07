---
name: bazi-platform-harness
description: 🚨 八字排盘平台·工程化落地总调度Harness。v7.6结构迁移：bazi代码迁入profile/projects/bazi-platform/（非profile根目录），skills直接在profile根目录(无symlink)，HERMES.md在profile根目录。路径示例：scripts/ → projects/bazi-platform/scripts/
category: software-development
tags: [八字, 排盘, 工程化, 校验, 流水线]
---

# 🏗️ 八字排盘平台 · 工程化落地总调度 Harness v7.6

> **2026-07-06结构迁移**：bazi代码迁入`profile/projects/bazi-platform/`。路径变化：
> - 旧：`/root/bazi-platform/scripts/bazi-must-run-engine.sh`
> - 新：`projects/bazi-platform/scripts/bazi-must-run-engine.sh`（从profile根目录起）
> - skills/直接位于profile根目录（不再symlink）
> - HERMES.md位于profile根目录（or链第1优先级）

> 金鉴真人的工程化身份：Orchestrator（拆任务+验结果）
> Sub-Agent分工、身份定义 → **SOUL.md（profile根目录·自动加载，不要手动读）**
> 老板画像、原则 → **USER.md（memories/USER.md·自动注入，不要手动读）**
> **本文件(HERMES.md)** = 项目级约束+SOP（or链最高优先级）
> **references/SOUL.md和references/USER.md** = skill内参考副本，非主要加载源

---

## ⚠️ 核心教训：Hermes加载机制是or链，不是叠加载

> 2026-07-06 我造了BOOTSTRAP.md + preflight.sh手动加载流程 → 被老板连续纠正4次
> 根源：我在设计机制前没先理解现有机制。

### 正确加载链（源码验证·prompt_builder.py L1955）

**两条独立线：**

**线A：系统级（独立加载，无条件）**
```
SOUL.md    ← profile根目录 · 自动加载 → 角色/原则/系统铁律
USER.md    ← memories/USER.md · 自动注入 → 老板画像/风格/教训
MEMORY.md  ← memories/ · 自动注入 → 持久记忆
```

**线B：项目级（or链——只加载1个，找到就停）**
```python
project_context = (
    _load_hermes_md(cwd_path, ...)   # .hermes.md / HERMES.md, 递归往上到git root
    or _load_agents_md(cwd_path, ...) # AGENTS.md, 只在CWD（不往上走！）
    or _load_claude_md(cwd_path, ...)  # CLAUDE.md
    or _load_cursorrules(cwd_path, ...) # .cursorrules
)
```

### ⚠️ 常见错误（禁止）

| 错误 | 为什么错 | 正确做法 |
|:-----|:---------|:---------|
| 造手动加载流程(BOOTSTRAP.md/preflight.sh) | Hermes已自动加载，重复造轮子 | **信任Hermes**，不手动读已自动加载的文件 |
| SOUL.md放项目目录 | 不会自动加载，放profile根目录才生效 | SOUL.md在`~/.hermes/profiles/jinjian-zhenren/` |
| AGENTS.md放项目根目录 | or链第2优先级，被.hermes.md挡路 | **用HERMES.md**（第1优先级） |
| bazi铁律放SOUL.md | SOUL.md是系统级，跨项目通用 | SOUL.md=系统身份+framing；HERMES.md=项目级约束+SOP |
| 叠加载想象 | 以为所有文件一起上 | 系统级独立 + 项目级or链，**不叠** |

---

## 🔥 物理铁律速查

| 铁律 | 内容 | 来源 |
|:----|:-----|:------|
| ① 排盘门禁 | `bash projects/bazi-platform/scripts/bazi-must-run-engine.sh` | 2026-06-29 |
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
| **㉑ 加载机制** | **SOUL.md(系统级)+HERMES.md(项目级)已分离。HERMES.md取代AGENTS.md（or链最高优先级）** | **2026-07-06** |
| **㉒ 起运精确计算** | **见下方"起运年龄精确计算与验证工作流"全量5关流程。起运年份：出生年+浮点月份偏移，Q4(10~12月)自动+1。禁用int截断+禁止写近似值** | **2026-07-07** |
| **㉓ 起运年份Q4进位** | **起运月份≥10(Q4) → 显示年份+1（大运只占当年尾巴，主要覆盖次年起的10年）** | **2026-07-07** |
| **㉔ 引擎da_yun.py禁用int()** | **da_yun.py中`int(qi_yun_age + step*10)`已删除。改用浮点月偏移+Q4进位。这是代码级bug，不是人为疏漏** | **2026-07-07** |

---

## 🧠 修正方法论（2026-07-07 老板校准）

> **核心教训**：修Bug时，必须先查原始理论知识规则，再看归档/旧版。**
> 老板说：「别看归档，你得看原始理论知识规则是啥」
> 老板说：「先补你的规则体系应用体系，再补报告」

```yaml
【修正三级流程】每次被指出Bug时：

第1级 — 查原始理论（不看归档/旧版）
  ✅ 先找原始素材：理论体系/金鉴真人八字命理_全量知识体系.md 等
  ✅ 逐字读原文规则（如「一天为四个月」）
  ✅ 从原文推导出正确的算法/公式
  ❌ 禁止：先看旧档案/旧报告怎么写的再用那个去凑
  ❌ 禁止：凭记忆写规则，必须回到原文

第2级 — 修规则体系+应用体系（先于报告）
  ✅ 先修理论知识库（理论体系/下的原始规则文本）
  ✅ 再修引擎代码（da_yun.py等.py文件）
  ✅ 再修模板（bazi-report-template SKILL.md里的公式）
  ✅ 最后：更新技能库（skill里的参考公式+铁律）
  ❌ 禁止：只改报告不改引擎和模板（治标不治本）
  ❌ 禁止：先改报告，回头再补引擎（顺序反了导致bug遗留）

第3级 — 验证调用链（2026-07-07新增·老板校准）
  🚨 关键问题：「每次排盘确定必会调用吗？」
  ✅ 检查：修复的代码在正常流程中是否真的被执行？
  ✅ 不是假设「应该被调用」——要找到物理证据：
     ┌─ 导入语句（from xxx import fix_fn）— 存在？
     └─ 调用点（fix_fn()在哪个文件哪一行）— 每次排盘必经？
  ✅ 如果没有物理入口 → 代码修了也没用，需补调
  ✅ 证据示例：「pipeline_v5.py L171: compute_da_yun(...) ← 唯一入口，每次跑」

第4级 — 验证+补报告
  ✅ 引擎验证通过后，用新引擎跑全量测试
  ✅ 用真实八字验证（家主/主母/子源各跑一遍）
  ✅ 最后更新报告（按新规则修正数据）
  ✅ 推库前过完整的验证流水线

第5级 — 双库同步提交（profile repo + knowledge base）
  ✅ 引擎/模板修改 → 提交到 profile repo（jinjian-zhenren）
  ✅ 报告修正 → 提交到 knowledge base（weiwuji-knowledge-base）
  ✅ 两句commit写清楚变更内容，不写模糊标题

口诀：先查理论再修码，引擎模板同步改
      调用链验证不能少，物理证据确认调
      不要看档案凑数，原文推导才是正
      修完引擎再报告，双库推库过流水线
```

### 修正与ALLNEW的区别

| 类型 | 触发语 | 依赖旧版 | 核心操作 |
|:-----|:-------|:---------|:---------|
| **修正** | 老板说「修正」「改一下」「这个不对」 | 保留旧版框架，改错误部分 | 先查理论→修引擎/模板→补报告 |
| **ALLNEW** | 老板说「全部重写」「重做」 | 不读旧版文件 | 从零重新推导全部内容 |

这个方法论来自2026-07-07老板的三次纠正循环（起运年龄int截断→Q4进位→时柱分析遗漏）:
- 第一次我先改了报告，但引擎代码没改 → 老板指出int()还在
- 第二次我没查原始理论先看归档 → 老板说「别看归档」
- 第三次我只补报告没先修规则/应用体系 → 老板说「先补你的规则体系应用体系」

## 📐 验证流水线

| 命令 | 说明 | 时机 |
|:-----|:------|:------|
| `python3 projects/bazi-platform/scripts/canggan-parse.py /tmp/bazi_last_result.json` | 排盘后自动调：藏干十神解析 + 易混淆标注 | 每次排盘后 |
| `python3 projects/bazi-platform/scripts/pillar-verify.py` | 四柱分析前跑：5关校验（五鼠遁/十神/结构/冲刑/最优性） | 分析发布前 |
| `python3 projects/bazi-platform/scripts/verify_report.py` | 报告发布前跑：7项格式校验 | 报告发布前 |
| `cd projects/bazi-platform/engine/tests && python3 validate_all.py` | 引擎全量验证 | 代码修改后 |

### 🚨 起运年龄精确计算与验证工作流（2026-07-07新增·3次纠正后的固化流程）

> **致命教训**：起运年龄已被纠正3次（2026-07-01/偏移1.6岁, 2026-07-05/int截断, 2026-07-07/近似值）。每次错因不同，每次后果都是15年流年表全错。

```yaml
【强制流程】每次涉及大运/起运年龄的输出，必须过以下5关：

第1关 — 引擎计算
  python3 -c "import sys; sys.path.insert(0,'projects/bazi-platform/engine'); \
    from da_yun import compute_qi_yun_days; \
    days=compute_qi_yun_days(YEAR, MONTH, DAY, '月支', is_shun=BOOL); \
    age=round(days/3,2); print(f'节气距离: {days}天 → 起运: {age}岁')"

第2关 — 公式显式校验（报告中必须写出）
  「{出生日期} → 交{节气名}({节气日期}) → 距离{days}天 → {days}÷3={age}岁」

第3关 — 起始年份校验（浮点偏移 + Q4进位，禁用int截断）
  ⚠️ 核心陷阱：`int(qi_yun_age + step*10)` 截断小数 → 大运偏移
    例：int(0.33)=0→start_year=1980❌（应1981·Q4进位）
    正解：用浮点月份偏移计算起运时间所在月份，不是int截断

  公式：
    起运年龄 = age (浮点)
    月份偏移 = round((age - int(age)) × 12)   # 例: 0.33→round(3.96)=4个月
    有效月 = 出生月 + 月份偏移
    年份进位 = 0; while 有效月>12: 有效月-=12; 年份进位+=1
    起始年 = 出生年 + int(age) + 年份进位
  
  Q4进位（起运在年底的特殊处理）：
    如果有效月 ≥ 10 (即10/11/12月)，起始年 += 1
    因为大运只占当年最后不到3个月，主要覆盖次年起的10年

  第n步年份 = [起始年+(n-1)×10, 起始年+(n-1)×10+9]

第4关 — 当前年份交叉验证（最重要！）
  取当前年份 - 出生年 = 命主当前周岁
  检查当前年龄落在哪个大运范围内
  核对报告中该大运标签与实际是否一致
  口诀：当前年份减出生，岁数落在哪步运
        报告标签核一遍，Q4进位别遗漏

第5关 — 大运序列完整性校验
  确认每步=10年：end_year - start_year + 1 = 10 ✅
  相邻步无间隔：下一运start_year = 上一运end_year + 1 ✅
  起运后正确排（顺/逆）到目标岁数（至少100岁即≥10步）

【常见错误列表】
  ❌ 错误1：写近似值("30岁起运") → 正确：「0.33岁起运」
  ❌ 错误2：int截断(出生年+int(0.33)=1980❌，正确是1981)
          int截断丢失月份信息：0.33年=4个月→从8月起+4月=12月→Q4→1981
  ❌ 错误3：偏移(把30.4~40.4写成32~41=偏移1.6岁→15年流年全错)
  ❌ 错误4：步数不够(只排到90岁而不是100岁)
  ❌ 错误5：节气跨年处理遗漏(12月交次年节气vs1月交上年节气)
  ❌ 错误6：只改大运列不改分析文本（大运切换后旧大运的分析断语必须同步更新）

口诀：起运年龄五关过，公式显式不能缺
      当前年份交叉验，步数覆盖到百岁
      节气天数÷3取精，浮点偏移+Q4进位
      int截断是致命，大运偏移毁十年
```

---

## 📂 本技能包含的文件

| 文件 | 说明 |
|:-----|:------|
| `references/SOUL.md` | 🔥 金鉴真人身份参考副本（实际自动加载版在profile根目录） |
| `references/USER.md` | 🔥 老板用户画像参考副本（实际自动注入版在memories/USER.md） |
| `references/engineering-checklists.md` | 工程检查清单 |
| `references/project-config.md` | 项目配置（含验证命令、铁律、测试速查） |
| `references/physical-pipeline-20260706.md` | 物理化流水线 |
| `references/full-chain-verification.md` | 全链路验证 |
| ...（另含19个参考文件） |

---

## ⚠️ 加载本技能时必须做的

1. `skill_view('bazi-platform-harness', 'references/project-config.md')` → 加载完整配置
2. **不要手动加载SOUL.md/USER.md** —— Hermes已在系统级自动加载
3. 排盘前: 确认`/tmp/bazi_last_result.json`已更新（由bazi-must-run-engine.sh生成）
4. 发布报告前: 跑`verify_report.py`确认格式通过
5. 四柱分析结论发布前: 跑`pillar-verify.py`确认5关全过
