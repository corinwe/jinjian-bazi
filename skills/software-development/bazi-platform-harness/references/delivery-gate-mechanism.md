# 金鉴真人·交付物理门禁机制（2026-07-07）

> 本文件记录「交付物理门禁」的完整设计思路、执行机制和实战验证结果。
> 核心教训：文件规则（SOUL.md/HERMES.md/SOP）不能替代物理阻断。LLM会「觉得差不多」就放行。

---

## 问题溯源

2026-07-07 为老板生成主母报告时，出现了三个本应被挡住的低级问题：

| 问题 | 原因 | 本该有的防御 |
|:-----|:-----|:-------------|
| 行数不足（238行） | 写了核心内容就交 | SOP里写了≥800行，但没物理执行 |
| 品牌名残留（金鉴真人×2） | 从模板复制没清理 | CHECKLIST里写了品牌名检查，没跑 |
| 缺性格分析 | 以为写够了，实际跳过了 | Phase 4.3五项必含里写了，没打勾 |

**根因**: 不是文件里没写规则，是「原则写进文件」≠「执行」。LLM在长任务中会遗忘/放松对自己的约束。

---

## 解决方案：双层硬约束

### 第1层：物理门禁脚本（`delivery-gate.py`）

13项检查，exit code阻断：

```
exit 0 = ✅ 全部通过，可以交付
exit 1 = ⛔ 阻断，先修复再重跑
```

**线A（引擎数据一致性·7项）**: 继承自 `verify_report.py` 的7项数据校验
| 编号 | 检查项 | 说明 |
|:----|:-------|:-----|
| A1 | 身强弱分数一致 | 报告中的分数±0.5以内 |
| A2 | 财星分数一致 | 报告中的分数±0.5以内 |
| A3 | 五行生克方向 | 防「金生土」写反为「土生金」 |
| A4 | 十神名称 | 防戊土对庚辛金写成偏印（应正印） |
| A5 | 大运年份 | 引擎数据与报告对照 |
| A6 | 喜忌一致性 | 引擎喜用/忌神列表与报告一致 |
| A7 | 空亡一致性 | 引擎空亡字段在报告中体现 |

**线B（/goal交付门禁·6项）**: 新增的硬约束
| 编号 | 检查项 | 阈值 |
|:----|:-------|:-----|
| G1 | 品牌名=0残留 | 0处（九龙道长/金鉴真人） |
| G2 | 五重人格全部存在 | 特质一~五全部出现 |
| G3 | 精简版≥800行 | ≥800行 |
| G4 | 婚姻子女提及≥5处 | ≥5处关键词 |
| G5 | 补财库方法≥5种 | ≥5种不同关键词 |
| G6 | 财星数字来自引擎 | 与引擎JSON一致 |

### 第2层：Hermes `/goal` 系统级硬约束

**原理**: Hermes内置的 `slash command`: `/goal <text>`

- 设置跨轮次持续性目标
- 每轮对话结束后，轻量级Judge模型自动检查目标是否达成
- 未达成 → Judge返回 `continue` → 系统强制Agent继续工作
- 已达成 → Agent可以正常交付

**用法**: 老板在Feishu打一次 `/goal 交付前必须通过delivery-gate.py》`，后续所有会话Judge自动检查。

**与Kanban的关系**: 
- `/goal` = 单Agent跨轮次的硬约束（解决「忘了执行」）
- Kanban = 多Agent/多角色的SOP编排
- 两者互补，不互斥

---

## 实战验证结果

在333行报告上跑门禁，成功阻断：
- ✅ G1/G2/G4/G5 通过（品牌名/性格/婚姻/补财库已正确）
- ✅ A1~A7 全部通过（引擎数据一致）
- ❌ G3 行数不足：334行 < 800行

扩展报告至800行后重跑，全部13项通过 ✅

---

## 2026-07-07 追加：两个结构性Bug发现的教训

### Bug 1：引擎JSON数据结构假设错误

**现象**：G5b(财库方位检查)对错误版本返回✅通过，对正确版本也返回✅通过——静默失效。

**根因**：`delivery-gate.py` 假设引擎JSON是嵌套结构 `engine["result"]["sec_X"]`，但 pipeline_v5 实际输出**扁平结构** `engine["sec_X"]`。A1~A7有fallback没暴露问题，G5b没有fallback直接失败（被try/except静默吃掉）。

同时 `sec_1_overview.ri_zhu` 是 dict `{"gan":"庚","wx":"金"}` 不是字符串，`ri_zhu[0]` 触发 KeyError。

**修复**：
```python
# 扁平+嵌套双兼容
s1 = engine.get("sec_1_overview", {}) or {}
# ri_zhu可能是dict也可能是字符串
if isinstance(ri_zhu, dict):
    ri_gan = ri_zhu.get("gan", "")
elif isinstance(ri_zhu, str) and ri_zhu:
    ri_gan = ri_zhu[0]
```

### Bug 2：函数体内同类代码残留

**现象**：修了函数开头 `ri_zhu[0]` 的提取，但没发现同一函数内还有第二处 `ri_gan = ri_zhu[0]`（line 295）。只修了第一处，第二处继续报错。

**根因**：点面体修复不到位——**应该在函数内全文搜索所有 `ri_zhu[0]` 同类模式，而不是只修第一个看到的。**

**修复**：找到函数内所有 `ri_zhu[0]`，统一用一个变量传递。

### 教训总结

| 维度 | 原做法 | 新做法 |
|:-----|:-------|:-------|
| **数据结构假设** | 假设一种结构就写死了 | 兼容扁平+嵌套，加fallback |
| **字段类型假设** | 假设ri_zhu是字符串 | isinstance检测dict/str |
| **同类代码删除** | 修一个点就走 | grep全函数找同类模式再修 |
| **try/except陷阱** | 静默吃掉异常 | 异常必须打印到输出，不能吞 |

## G5b新增：财库方位语义检查

从纯关键词检查升级为「关键词+方位语义」检查：

```python
CAI_KU_FANGWEI = {
    '庚': '西南', '辛': '西南',  # 庚辛金→财=木→木库=未(西南)
    ...
}
```

在财库段落内扫描方位词，与日主对应的正确方位比对。错误方位被正确拦截。

---

## 涉及文件

| 文件 | 路径 | 说明 |
|:-----|:-----|:------|
| delivery-gate.py | `projects/bazi-platform/scripts/delivery-gate.py` | 13项检查物理门禁 |
| run-with-gate.sh | `projects/bazi-platform/scripts/run-with-gate.sh` | 一键触发包装脚本 |
| verify_report.py | `projects/bazi-platform/scripts/verify_report.py` | 原有7项引擎数据校验 |
| bazi-paipan-sop | `skills/bazi-paipan-sop/SKILL.md` | SOP Phase 5已集成门禁流程 |
| bazi-platform-harness | `skills/software-development/bazi-platform-harness/SKILL.md` | Harness铁律㉕㉖ |
