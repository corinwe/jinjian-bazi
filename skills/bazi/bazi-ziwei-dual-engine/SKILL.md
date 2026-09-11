---
name: bazi-ziwei-dual-engine
description: Use when 排盘/命理分析/写报告. 八字×紫微双引擎默认合参。
tags: [八字, 紫微, 第四引擎, 双引擎, 合参, 物理门禁, 铁律]
related_skills: [bazi-paipan-sop, bazi-ziwei, bazi-auto-verify, bazi-report-template]
---

# 八字 × 紫微 · 双引擎默认合参体系（老板2026-09-10指令）

## 🚨 核心铁律

> 老板原话：「紫微做成正式平台第四引擎。**每跑一个八字，默认都要自动结合我们已有的八字技能和紫微分析放在一起进行评估**。除非我特别说明：①只用传统的八字，不用紫微；②只用紫微，不用传统的八字。」

| 情形 | 行为 |
|:---|:---|
| **默认（无需任何说明）** | 八字 + 紫微 **双引擎同时跑**，报告含紫微专章 + 交叉印证专章 |
| 老板说「只用八字」 | 加 `--bazi-only`，可省紫微 |
| 老板说「只用紫微」 | 加 `--ziwei-only`，可省八字 |
| 未获明确说明 | ❌ 不得单引擎、不得跳过紫微（嫌慢也不行） |

## 唯一入口（强制）

```bash
cd /root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform
bash scripts/bazi-dual-prepare.sh <姓名> <性别> <YYYY-MM-DD> <HH:MM> [出生地]
#   → /tmp/{名}_ds.json      (八字数据源)
#   → /tmp/{名}_ziwei.json   (紫微数据源·第四引擎)
#   → 自动四柱交叉校验；不一致 exit 2（禁止出报告）
touch /tmp/.bazi_verified      # 写报告前的验证标记（一次性）

# 豁免（仅老板明确说明时）
bash scripts/bazi-dual-prepare.sh <姓名> <性别> <日期> <时间> --bazi-only
bash scripts/bazi-dual-prepare.sh <姓名> <性别> <日期> <时间> --ziwei-only
bash scripts/bazi-dual-prepare.sh --reset    # 恢复默认双引擎
```

## 物理门禁（规则写进文件≠被遵守，拦截才算数）

`pre_tool_call` hook → `/root/.hermes/hooks/bazi-mandatory/precheck.py`（v2.0/2.1）
拦截 `write_file`/`patch` 写报告（`/tmp/*报告*.md`、`人物档案/*`、`reports/`）：

| 触发条件 | 结果 |
|:---|:---|
| 无 `BAZI_DATASOURCE` / ds 文件不存在 | ⛔ block |
| 缺 `/tmp/{名}_ziwei.json` | ⛔ block（提示双引擎铁律 + 如何豁免） |
| 紫微与八字四柱**不一致** | ⛔ block（源头数据错误最后一道闸） |
| 缺 `/tmp/.bazi_verified` | ⛔ block（放行后标记被消费，一次一用） |
| 技能/文档 .md（非报告路径） | ✅ 放行（v2.1 已收窄，免误伤） |

## 第四引擎技术栈

```
engine/ziwei_engine.py    紫微引擎主程序 → /tmp/{名}_ziwei.json
engine/ziwei_bridge.js    iztro 2.6.1(MIT) 直连桥接层，命主/身主/12宫字段完整
skills/bazi/bazi-ziwei/   三方CLI（真太阳时校准：经度差+均时差）
           └ 严禁使用 dzcmemory-web/bazi-ziwei-skill（2026-08-25 被 GitHub DMCA 封禁）
```

输出内容：五行局 · 命主/身主 · 生年四化 · 十二宫（干支/主星+庙旺+四化/辅星/杂曜/大限/长生12神/博士12神）· 真太阳时校准 · 四柱交叉校验。

## 🚨 四柱交叉校验的口径归一化（2026-09-11 修复·小静 2007-04-13 案暴露）

**现象**：`bazi-dual-prepare.sh` 报「🚨 双引擎四柱不一致」并 exit 2，无法出报告。
实测差异 = 月柱：紫微侧 `丁亥 癸卯 丁丑 丙午` vs 八字侧 `丁亥 甲辰 丁丑 丙午`。

**根因（不是 bug，是两套月柱口径）**：
- 紫微侧 iztro 的 `chineseDate` 月柱按 **农历月** 定（正月=寅、二月=卯…）——紫微斗数传统口径；
- 八字侧 `engine/jieqi.py` 月柱按 **节气** 定（立春换年·节换月）；
- 当「农历月 ≠ 节气月」时（如 2007-04-13＝农历二月廿六，但 4/5 清明后已入辰月）**必然不等**。
- 家族五人（家主/主母/少爷/七七/左左）当年没暴露，是因为他们的农历月恰好等于节气月（巧合，非机制）。

**修复**（`engine/ziwei_engine.py` 新增 `_cross_check()`）：
1. **年/日/时柱必须严格一致**（真错误 → 仍拦截）；
2. 月柱先严格比；不等时用「五虎遁(年干) + 农历月」反算**期望月柱**：
   - 对得上 → **放行**，并在 `说明` 里标注「✅ 双引擎一致（口径差异已归一化）：紫微月柱X=农历N月口径·八字月柱Y=节气口径」；
   - 对不上 → **仍判不一致并阻断**（真错误）。
3. `四柱交叉校验['紫微引擎']` 会带 `(农历月口径)` 后缀以示区分。

**回归自测（改完必跑）**：
```bash
python3 -c "
import sys; sys.path.insert(0,'engine'); import ziwei_engine as Z
print(Z._cross_check('丁亥癸卯丁丑丙午','丁亥甲辰丁丑丙午',2007,4,13,12,0))  # 口径差异→True
print(Z._cross_check('丁亥癸卯丙子丙午','丁亥甲辰丁丑丙午',2007,4,13,12,0))  # 日柱错→False
print(Z._cross_check('丁亥乙卯丁丑丙午','丁亥甲辰丁丑丙午',2007,4,13,12,0))  # 月柱无法解释→False
"
```
**守则**：口径差异可以归一化，**真错误绝不放行**；遇到不一致先看是不是月柱，再判断是真错还是口径。

## 报告结构（双引擎模式）

1. 八字部分：照 21§ 模板（不变）
2. **紫微并列专章**：命身宫 / 三方四正 / 生年四化落宫 / 大限流年
3. **交叉印证专章（强制）**：≥6 组对照表

| 维度 | 八字依据 | 紫微依据 | 印证结论 |
|:---|:---|:---|:---|
| 格局·性格主轴 | 十神+格局 | 命宫主星+庙旺 | 一致/互补/存疑 |
| 事业·财富 | 财官星+旺衰 | 官禄宫+财帛宫+四化 | … |
| 婚姻 | 配偶宫+妻星 | 夫妻宫三方四正 | … |
| 父母/子女/健康/大运 | … | … | … |

**冲突必须标注「⚠️双引擎分歧」并给出取舍理由**（老板辩证思维铁律⑥：不全盘接受任何单一体系）。

## 已验案例（可回归）

| 命主 | 四柱 | 紫微要点 |
|:---|:---|:---|
| 七七（2017-07-07 08:00 女） | 丁酉 丁未 乙未 庚辰 | 金四局·命主文曲/身主天同·命宫武曲七杀·田宅天机化科·疾厄太阴化禄·子女巨门化忌 |
| 凤（1978-12-13 21:00 女） | 戊午 甲子 己酉 乙亥 | 三引擎一致（1988版已作废·见KB勘误） |

## Pitfalls（踩过的坑）

1. **紫微三方CLI会丢字段**：`bazi_ziwei_cli.js` 输出没有 `soul/body`（命主/身主）与 `decadalRange` → 必须走自建 `ziwei_bridge.js`，别直接解析三方CLI。
2. **星曜字段类型不定**：iztro 桥接层星曜可能是对象也可能是裸字符串 → 解析必须兼容两种。
3. **真太阳时校准用三方CLI**（有经度差+均时差），紫微命盘用自建桥接层 —— 两者互补，别只走一条路。
4. **写报告前不 touch `.bazi_verified`** → 必被 hook 拦；该标记一次性，写一份报告就失效一次。
5. **豁免标记是"老板授权"的物化**：不得自行创建 `.bazi_only`/`.ziwei_only`，只能在老板明确说明后创建。
6. **双引擎四柱不一致 = 停止工作**：先跑 `python3 scripts/bazi-jieqi-regression.py --quick`，查 `engine/jieqi.py` 节气定界，修好再出报告。

## 🚨 门禁接线陷阱（2026-09-10 血泪·必读）

**hook payload 的参数字段名是 `tool_input`，不是 `args`。**
读错字段 → 拿到空路径 → **门禁静默放行一切**，看起来"有门禁"其实从没拦过。
（同类历史事故：知识库 pre-commit 旧版门禁从未拦截过任何中文报告。）

| 陷阱 | 正确做法 |
|:---|:---|
| `payload.get("args")` | ✅ `payload.get("tool_input")`（并保留 args/tool_args/parameters/arguments/input/params 兼容链） |
| 依赖 `BAZI_DATASOURCE` 环境变量 | ❌ hook 是**独立子进程**，会话里 export 的变量传不进去 → ✅ **直接校验磁盘产物** `/tmp/{名}_ds.json` + `_ziwei.json` + 四柱一致 |
| 只测门禁逻辑（手工喂 JSON） | ✅ 必须**端到端实测**：真的写一个报告文件，确认被 block |

**验证门禁是否真活的唯一方法**：
```bash
rm -f /tmp/.bazi_verified
# 然后尝试 write_file /tmp/门禁测试_报告.md —— 必须被 block，否则门禁是死的
```
调试时 precheck.py 会把真实 payload 落到 `/tmp/hook_raw_payload.json`。

## 紫微细断层（2026-09-10 建立·与八字21§等重）

| 组件 | 作用 |
|:---|:---|
| `engine/ziwei_rules.py` | 规则库：**14主星×12宫=168条** + 四化48条 + 辅星14 + 格局13，全部**术语+白话双栏** |
| `engine/ziwei_star_combo.py` | 组合断层：**24组双星同宫断**（紫微天相/日月同宫/武曲天府…穷举完备）+ **17条三方四正组合规则**（三奇加会/双禄交流/禄马交驰/杀破狼联动/空劫入局/煞忌交加…）+ `double_star_of()`/`sanfang_combo()` 识别函数 |
| `engine/ziwei_weight.py` | **叠加权重层（量化）**：主星性质分×庙旺系数 + 双星加成 + 辅星吉煞分 + 四化分 → 单宫分(0-100)；领域总评＝本宫55%+三方各15%；输出三大王牌(≥75)/三大短板(≤35)/四级叠加特殊组合(煞忌交加·空转·虚旺·硬拼可用·桃花过旺·库星入库)/当前大限激活。**参数区可调**；断语文本来自规则库，本层只做排序与重点识别（不单独作断命依据）。启动时自动加载 `ziwei_weight_calib.json`（标定参数 BASE/a/b/c/d/k）。 |
| `engine/ziwei_liunian.py` | **流年权重层**：流年命宫（流年地支＝太岁定位）+ 流年四化飞入本命宫位（10干标准四化表）+ 生年四化**同星同化/双忌叠宫**警示 + 大限&流年双激活 + 六冲六合引动。输出某年主战场/吉凶落点/被动引动。 |
| `scripts/calibrate_ziwei_weight.py` | **系数标定器（双引擎一致性）**：以**八字引擎**同维分级（wealth/property/career/marriage/children/health）为观测标签，两级网格搜索（目标＝最大化强/中/弱方向一致数 → 最小 RMSE → 正则防过拟合）。产出 `ziwei_weight_calib.json` + 标定说明。当前：18标签，方向一致 **6/18→10/18**，RMSE 21.25→18.18。 |
| `engine/jixiong.py` | **吉凶评级模块（老板要求：白话必须说好坏与程度）**。① 倾向层（静态可复核）：`STAR_PALACE_LEVEL` 14主星×12宫=168条 + `DOUBLE_STAR_LEVEL` 24组 + `SANFANG_LEVEL` 17条 + 辅星 + 四化；② 程度层（按盘）：庙旺 + 吉煞辅星 + 四化 → 很强/较强/中等/偏弱/很弱。统一输出 `**【吉·较强】**`。阈值：大吉≥85 吉≥75 小吉≥62 平≥48 凶≥35 大凶<35。已覆盖 §0导读/§22.2/§22.4/§22.6/§22.7/§22.9/§22.10/§23（每份报告 207–215 个标签）。 |
| `engine/ziwei_detail.py` | 渲染器：`plain_intro`(§0白话导读) / `ziwei_detail_section`(§22逐宫细断+四化飞星+格局识别+大限) / `cross_section_plain`(§23带人话栏) |
| `engine/plain_glossary.py` | 术语快查 **54条**（八字40+紫微14：术语本义 + 说人话 + 怎么办） |
| `scripts/postprocess_dual_reports.py` | 后处理接线：21§引擎报告 → 双引擎+白话全量版 |

**全量版报告最终结构**：
```
【机制链注入】+ PIPELINE-SIG + 数据源对齐块(DS['字段']×8)
→ §0 白话导读（性格/事业/钱/婚/娃/健康/欠债处 + 术语快译）
→ §1–§21 八字全量（引擎深度版）
→ §22 紫微细断专章（22.1命盘 / 22.2逐宫细断 / 22.3宫义速查 / 22.4四化飞星 / 22.5格局识别 / 22.6大限细断）
→ §23 交叉印证专章（8+1行，每行带「人话结论」栏）
→ 附录A 术语快查
```

**生成命令（三人份实测 1948–1964行，全门禁通过）**：
```bash
cd /root/.hermes/profiles/jinjian-zhenren
touch /tmp/.bazi_verified
python3 scripts/gen_family_reports.py 家主 主母 少爷        # 21§引擎全量
cd projects/bazi-platform
python3 scripts/postprocess_dual_reports.py 家主 主母 少爷  # 注入拼音+白话+§22/§23
python3 /root/.hermes/profiles/jinjian-zhenren/scripts/verify-report-quality.py /tmp/家主_报告_双引擎.md
```

**知识库 pre-commit 报告门禁硬指标**（不过就拒提交，别用 --no-verify）：
≥800行 · §1–§21齐全 · 无空§ · **`DS['字段']` 直引 ≥3处**（写成"数据源见xxx"不算，必须 `DS['八字']` 这种形式）。

## 开发陷阱（写Python生成命理文本必看）

1. **中文引号写成英文引号 → SyntaxError**：命理白话里高频出现 `要修"舍得"`、`走"熬出来"的路`，写进 Python 双引号字符串会截断 → **一律用「」**。
   自查：`python3 -c "..."` 逐行统计 `"` 个数，`>=4 且非文档字符串` 的行必查。
2. **ds schema 有两套**：`bazi-data-source.py` 产出 `大运: list[dict]`；`convert_v5_to_ds.py` 产出 `大运: dict`（含"序列"） → 取值必须写兼容函数 `_dayun_list()`，否则 `'str' object has no attribute 'get'` / `unhashable type: 'slice'`。
3. **JS/命令行内联过大 payload 会被 hardline 拦**：长 heredoc 命令被 block 是**体积问题不是权限问题** → 按提示 `bash /root/.hermes/profiles/jinjian-zhenren/cache/blocked-scripts/blocked-*.sh` 直接跑落盘脚本。
4. **知识库 pre-commit 元文档豁免**：豁免分支为 `勘误*|说明*|README*|索引*|目录*|*模板*|_*|ARCHIVE_*` —— 匹配的是**文件名（basename）开头**。
   标定说明/方法论说明类文件必须**以「说明」二字开头**（如 `说明-紫微权重层系数标定_20260910.md`）；
   命名为 `00-标定说明_xxx.md` ❌ 不豁免（开头是 00-）→ 会被要求【机制链注入】而拒提交。
   **不要为了让门禁过而给非引擎产物硬加【机制链注入】标记**（那是溯源的假声明）；改名归位到正确类别才对。
5. **流程总览（八层）**：`单星单宫(168) → 双星同宫(24) → 三方组合(17) → 格局(13) → 量化权重(王牌/短板+大限激活) → 系数标定(双引擎一致性) → 流年(太岁+四化+冲合) → 吉凶评级(倾向×程度)`。
6. **吉凶标注两个易错点**（2026-09-10 实测踩到）：
   - **别用「领域总评」出标签**：领域总评＝本宫55%+三方各15%，被摊平（多在45–60）→ 标签全挤成「平」。出标签用**单宫分**。
   - **别把生年四化当「双忌叠加」**：生年化忌本身不算叠加；只有**同宫出现 ≥2 个同色四化**（或流年化忌落本命化忌宫）才算加重。
7. **V4A patch 偶发「Binary file」误报**：在含 `›`、`【】` 等符号的紧凑 Python 常量块上，`mode=patch` 可能报 binary 而拒绝。改用 `mode=replace` 或直接 python 读写文本替换（两者都稳）。

