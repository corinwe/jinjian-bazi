---
name: bazi-data-source
description: 金鉴真人·八字数据源验证+锁定体系。engine.json → bazi-data-source.py → datasource.json(23字段:8字段/藏干/藏干十神/纳音/空亡/神煞/起运年龄/8大运)。所有报告模块从datasource.json取数，物理禁止凭记忆重算。
tags: [八字, 数据源, 引擎, 排盘, 物理化, 约束]
related_skills:
  - bazi-paipan-sop
  - bazi-engine-workflow
  - bazi-foundation-analysis
references:
  - scripts/bazi-data-source.py — 验证+锁定脚本(engine→datasource)
  - scripts/report-generator.py — 数据源驱动的报告生成器
---

# 八字数据源体系 · 金鉴真人

> **🚨 铁律：数据源是唯一源泉。所有报告模块只能从 datasource.json 取数，禁止凭记忆/重算。**
>
> **老板指定架构**：
> ```
> Engine CLI → engine.json → bazi-data-source.py → datasource.json → 各模块取数+规则匹配
>               (16字段)       (验证+锁定+补全)      (23字段·唯一源)   (事业规则/财富规则/大运规则)
> ```

## 数据源字段清单

| # | 字段名 | 来源 | 类型 | 用途 |
|:-:|:-------|:-----|:-----|:-----|
| 1 | 年干 | ENGINE['四柱'] | str | 8字段·天干 |
| 2 | 年支 | ENGINE['四柱'] | str | 8字段·地支 |
| 3 | 月干 | ENGINE['四柱'] | str | 8字段·天干 |
| 4 | 月支 | ENGINE['四柱'] | str | 8字段·地支 |
| 5 | 日干 | ENGINE['四柱'] | str | 8字段·天干 |
| 6 | 日支 | ENGINE['四柱'] | str | 8字段·地支 |
| 7 | 时干 | ENGINE['四柱'] | str | 8字段·天干 |
| 8 | 时支 | ENGINE['四柱'] | str | 8字段·地支 |
| 9 | 藏干 | ENGINE['藏干'] | dict | 4个地支的藏干列表 |
| 10 | 藏干十神 | calc(藏干,日主) | dict | 每个藏干成分的十神标记 |
| 11 | 十神(天干) | ENGINE['十神'] | dict | 年干/月干/日干/时干的十神 |
| 12 | 纳音 | ENGINE['纳音'] | dict | 年柱/月柱/日柱/时柱 |
| 13 | 空亡 | calc(日柱干支) | str | 日柱对应旬空 |
| 14 | 日主 | ENGINE['日主'] | str | 日干 |
| 15 | 日主五行 | ENGINE['日主五行'] | str | 金木水火土 |
| 16 | 性别 | ENGINE['性别'] | str | 男/女 |
| 17 | 八字 | ENGINE['八字'] | str | 4柱用空格分隔 |
| 18 | 身强弱总分 | ENGINE['身强弱']['总分'] | float | 身强弱评分 |
| 19 | 身强弱等级 | ENGINE['身强弱']['等级'] | str | 身强/身弱/从弱/中和 |
| 20 | 起运年龄 | ENGINE['大运']['起运'] | str | 文字描述 |
| 21 | 起运年龄(岁) | ENGINE['大运']['起运年龄'] | float | 数值 |
| 22 | 神煞 | calc(日干,年支) | dict | 8种主要神煞 |
| 23 | 大运 | ENGINE['大运']['序列'] | list | 8步大运(到80岁) |

## 🚨 铁律：9种神煞检查顺序

神煞计算顺序固定：天乙贵人→文昌贵人→桃花→驿马→华盖→孤辰寡宿→灾煞。每种神煞有独立的查表（日干/年支两种口径）。注意：文昌贵人用日干查，桃花用年支查，不可混用。

## 🚨 铁律：体用穷举必须同时列天干+藏干（2026-07-16 子源校准）

> **根因**：report-generator.py 只从DS['藏干十神']提取财官为用，漏算天干财官（年干辛正财8分+月时双癸正官24分=32分）。
> **结果**：子源用被算成14.4分（×），正确46.4分（√）。体用比6.78:1→2.62:1。
> **教训**：体用穷举表必须同时列出天干成分和藏干成分。

```python
# ✅ 正确：天干财官+藏干财官=用
# 天干财官：年干8分 + 月干12分 + 时干12分
# 藏干财官：各藏干按比例折算
def calc_yong(DS):
    yong = {'正财':0,'偏财':0,'正官':0,'七杀':0}
    # ① 天干财官
    for pos in ['年','月','时']:
        ss = DS['十神'][pos]
        if ss in yong:
            yong[ss] += 8.0 if pos == '年' else 12.0
    # ② 藏干财官
    for zk in ['年支','月支','日支','时支']:
        for c in DS['藏干十神'][zk]:
            if c['十神'] in yong:
                yong[c['十神']] += 12 * int(c['比例'].replace('%','')) / 100
    return sum(yong.values())
```

## 🚨 铁律：大运顺逆看年干阴阳（非日干）

```python
# 🔴 错误历史：2026-07-16 魏启令八字用日干(辛=阴)定顺逆 → 判逆排 → 大运顺序全反
# ✅ 正确：年干阴阳 + 性别
is_shun = (YY_MAP[nian_gan] == '阳' and gender == '男') or \
           (YY_MAP[nian_gan] == '阴' and gender == '女')
# 年干阳男/阴女→顺排；年干阴男/阳女→逆排
```

## 🚨 铁律：8大运足够（不扩展到10步）

老板指定：8步大运（到80岁）足够分析一生。扩展逻辑仅在引擎输出少于8步时补足。

## 物理约束机制（4层）

### 约束① — inject-context.sh 自动设置 BAZI_DATASOURCE

```bash
# pre_llm_call hook：每次LLM调用前自动检测并设置
if [ -z "$BAZI_DATASOURCE" ]; then
    for f in /tmp/*_ds.json; do
        [ -f "$f" ] && export BAZI_DATASOURCE="$f" && break
    done
fi
```
不设置 → pre_tool_call_hook阻止写报告。

### 约束② — precheck.py 物理拦截

在 `/root/.hermes/hooks/bazi-mandatory/precheck.py` 中嵌入：
```
检查顺序：
  ① /tmp/.bazi_verified 存在？→放行
  ② BAZI_DATASOURCE 已设置？→不满足→BLOCK
  ③ BAZI_DATASOURCE 文件存在？→不满足→BLOCK
  ④ 全部通过→继续走原拦截逻辑
```

### 约束③ — report-generator.py

所有模块函数的唯一参数是DS（数据源dict）。
```python
def module_wealth(DS):     # 财富模块
    cai = DS['藏干十神']    # 读文件数据，非记忆
def module_career(DS):     # 事业模块  
    guan = DS['藏干十神']
def module_dayun(DS):      # 大运模块
    dy = DS['大运'][i]     # DS['大运']来自汽车引擎输出，非临时计算
```

### 约束④ — Phase 5.1 内容对齐校验

| 检查项 | 比对源 | 历史错误 |
|:-------|:-------|:---------|
| 身强弱得分 | ENGINE['身强弱']['总分'] | 子源55.6分(中和)被写成身强 |
| 身强弱等级 | ENGINE['身强弱']['等级'] | 同上 |
| 大运年龄 | ENGINE['大运']['序列'][i]['起始年龄'] | 戊子运真/假误判 |
| 日主 | ENGINE['日主'] | 无 |
| 藏干 | ENGINE['藏干']存在 | 申中戊(余气30%)被遗忘 |

## 🚨 铁律：每份报告用各自数据源独立生成（2026-07-16 主母复制Bug校准）

> **根因**：生成主母成+子源报告时，复制魏启令报告模板只替换了名字，未替换八字数据。
> **结果**：主母成的报告正文全是魏启令的数据（辛金身强→实际应为庚金从弱）。
> **教训**：**永远不要复制一份报告当模板改名字**。每份报告必须从其各自的数据源独立生成。

```python
# 🔴 错误（2026-07-16 主母复制Bug）
for name in ['主母成', '子源']:
    shutil.copy('魏启令_报告.md', f'{name}_报告.md')  # ← 只改了文件名，数据没换！
    # 然后替换名字字符串 → 数据仍然是魏启令的

# ✅ 正确
for name, ds_path in [('主母成', '/tmp/cheng_ds.json'), ('子源', '/tmp/ziyuan_ds.json')]:
    DS = json.load(open(ds_path))          # 从该人自己的数据源读
    generate_report(DS, name)              # 用该人自己的数据生成
```

**验证方法**：每份报告生成后立即检查——
- 报告中八字=该人八字？→ `if label == '主母成': assert '丁卯丁未庚午壬午' in content`
- 报告中不包含他人的八字？→ `assert '庚申癸未辛亥辛卯' not in content` （魏启令八字）
- 报告中日主=该人日主？→ `assert R+'金' in content` （主母成为庚金）

## 🚨 铁律：报告中每个数字必须标记数据源路径（Phase 5.1）

源于2026-07-16子源校准：子引擎报告身强弱的子代理写身强，无物理约束阻止。

格式：
```markdown
- 身强弱：64.0分（DS['身强弱']['总分']）
- 大运：甲申（DS['大运'][0]）
- 财星：乙木偏财（DS['藏干十神']['时支'][0]）
```

报告尾部统一声明：
```
**数据源**：/tmp/{姓名}_ds.json
**所有数字来自DS路径** | **0处凭记忆数据**
```

## 🚨 铁律：报告必须通过质量门禁才能推库（Phase 5.6）

```bash
# 推库前必须运行
python3 /root/.hermes/profiles/jinjian-zhenren/scripts/verify-report-quality.py /tmp/{姓名}_报告.md
# exit 0 → 可推库
# exit 1 → 修复后重新验证
```

质量门禁5项检查：
1. ✅ 文件存在且非空
2. ✅ 行数 ≥ 800行（G3门禁）
3. ✅ 21§完整性（§1-§21全部有内容）
4. ✅ 每个§有分析性文本（非空§）
5. ✅ 数据源引用 ≥ 3处（DS['xxx']格式）

## 相关脚本

| 脚本路径 | 用途 | 此session更新 |
|:---------|:-----|:--------------|
| `/root/.hermes/profiles/jinjian-zhenren/scripts/bazi-data-source.py` | 引擎→数据源验证+锁定 | v2.2:8大运+神煞+空亡 |
| `/root/.hermes/profiles/jinjian-zhenren/scripts/report-generator.py` | 从DS取数的报告生成器 | 修复:天干财官计入用 |
| `/root/.hermes/profiles/jinjian-zhenren/scripts/verify-report-quality.py` | 报告质量物理门禁(21§/≥800行) | 本次新增 |
| `/root/.hermes/hooks/bazi-mandatory/precheck.py` | pre_tool_call物理拦截(BAZI_DATASOURCE检查) | 本次新增嵌入 |
| `/root/.hermes/hooks/bazi-mandatory/inject-context.sh` | pre_llm_call自动设BAZI_DATASOURCE | 本次更新 |

## 使用流程

```bash
# 1. 跑引擎 → engine.json
python3 bazi-engine.py <出生参数> --json > /tmp/{姓名}_engine.json

# 2. 数据源验证+锁定 → datasource.json
python3 bazi-data-source.py /tmp/{姓名}_engine.json /tmp/{姓名}_ds.json

# 3. 设置环境变量（物理约束）
export BAZI_DATASOURCE=/tmp/{姓名}_ds.json

# 4. 各模块从数据源取数
python3 report-generator.py {姓名} 所有模块
```

## 各模块取数对照

| 模块 | 从数据源取 | 对应的规则技能 |
|:-----|:-----------|:---------------|
| 体用分析 | DS['身强弱']+DS['藏干十神'] | bazi-foundation-analysis §3B/§3A.9 |
| 大运分析 | DS['大运']+DS['藏干']+DS['年干'] | bazi-engine-workflow |
| 财富分析 | DS['藏干十神'](财+库) | bazi-wealth-analysis |
| 事业分析 | DS['藏干十神'](官杀) | bazi-career-analysis |
| 婚姻分析 | DS['日支']+DS['藏干十神'] | bazi-marriage-analysis |
| 神煞分析 | DS['神煞'] | bazi-foundation-analysis §13 |
| 纳音分析 | DS['纳音'] | bazi-foundation-analysis §11 |
| 空亡分析 | DS['空亡'] | bazi-foundation-analysis §空亡 |
