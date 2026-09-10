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
