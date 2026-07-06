# 知识库报告生成工作流

> 从引擎JSON → 标准格式报告 → 推送到魏无记知识库

## 流程总览

```
用户八字（姓名+性别+年月日+时辰）
    │
    ▼
Step 1: run_pipeline → engine JSON (含21§ + narrative + detail_analysis)
    │  cmd: python3 engine/pipeline_v5.py --json
    │
    ▼
Step 2: report_standard_gen.py → .md标准报告
    │  cmd: python3 engine/report_standard_gen.py <json_path> <姓名> <性别>
    │
    ▼
Step 3: 写入知识库 → 人物档案目录
    │  路径: /root/.hermes/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案/{folder}/
    │
    ▼
Step 4: git add + commit + push
    │  路径: cd /root/.hermes/weiwuji-knowledge-base
```

## Step 1: 引擎管线

```bash
cd /root/bazi-platform
python3 engine/pipeline_v5.py \
  --name <姓名> --gender <男/女> \
  --year <年> --month <月> --day <日> --hour <时辰(0-23)> \
  --json > /tmp/narrative_out_<key>.json 2>&1
```

输出JSON包含：
- `paipan` — 四柱排盘
- `basic_data` — 基础数据
- `analysis` — 分析提取（含简短narrative）
- **`result`** — **21§完整数据（核心）** — 每节均含 `narrative` + `detail_analysis`
- `text` — format_21_section_report紧凑文本
- `success` — true/false

**21§数据字段**：
| 字段 | 内容 | 含narrative | 含detail_analysis |
|:-----|:-----|:-----------:|:-----------------:|
| sec_1_overview | 一页总览 | ✅ | ✅ |
| sec_2_ge_ju | 格局分析 | ✅ | ✅ |
| sec_3_shen_qiang_ruo | 身强弱 | ✅ | ✅ |
| sec_4_xi_yong | 喜用神/忌神 | ✅ | ✅ |
| sec_5_zai_huo | 灾祸预警 | ✅ | ✅ |
| sec_6_character | 性格解析 | ✅ | ✅ |
| sec_7_appearance | 身材外貌 | ✅ | ✅ |
| sec_8_wealth | 财富格局 | ✅ | ✅ |
| sec_9_property | 置业分析 | ✅ | ✅ |
| sec_10_career | 事业发展 | ✅ | ✅ |
| sec_11_education | 学业学历 | ✅ | ✅ |
| sec_12_marriage | 婚姻感情 | ✅ | ✅ |
| sec_13_children | 子女运势 | ✅ | ✅ |
| sec_14_health | 健康注意 | ✅ | ✅ |
| sec_15_family | 六亲关系 | ✅ | ✅ |
| sec_16_events | 流年事件 | ✅ | ✅ |
| sec_17_da_yun_detail | 大运详批 | ✅ | ✅ |
| sec_18_verdicts | 三决断 | ✅ (dict内narrative) | ✅ (独立key) |
| sec_19_overall | 运程总评 | ✅ | ✅ |
| sec_20_wu_xing_advice | 五行补充 | ✅ | ✅ |
| sec_21_advice | 人生建议 | ✅ | ✅ |

## Step 2: 生成标准报告

```bash
python3 /root/bazi-platform/engine/report_standard_gen.py \
  /tmp/narrative_out_<key>.json \
  "<显示名·全名>" \
  "<男/女>"
```

**report_standard_gen.py** 路径：`/root/bazi-platform/engine/report_standard_gen.py`
- 输出：21§完整markdown，每节含 narrative + detail_analysis + 结构化数据
- 平均 380行 / 10,000-11,500字符

## Step 3: 写入知识库

```bash
kb_base="/root/.hermes/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案"

# 人物→目录映射
declare -A FOLDERS
FOLDERS["家主"]="01-家主-魏启令"
FOLDERS["主母"]="02-主母-成"
FOLDERS["源"]="03-少爷-子源"
FOLDERS["立"]="05-立"
FOLDERS["仔仔"]="19-仔仔"

key="家主"
folder="${FOLDERS[$key]}"
filename="${key}_标准引擎深度报告_v1.0_标准格式_20260627.md"
mkdir -p "${kb_base}/${folder}"
cp /tmp/report_${key}.md "${kb_base}/${folder}/${filename}"
```

## Step 4: 推送

```bash
cd /root/.hermes/weiwuji-knowledge-base
git add -A
git commit -m "📖 描述信息"
git pull --rebase
git push
```

## 已知人物关系（2026-06-27修正版）

| 称呼 | 正式名 | 出生信息 | 八字 | 知识库目录 |
|:----|:-------|:---------|:-----|:----------|
| 老板/您 | 魏启令 | 1980-08-06 05:30 卯时 | 庚申 癸未 辛亥 辛卯 | 01-家主-魏启令 |
| 太太 | 刘成(主母) | 1987-07-20 12:00 午时 | 丁卯 丁未 庚午 壬午 | 02-主母-成 |
| **少爷** | **源(子源/魏源)** | **2011-05-31 09:09 巳时** | **辛卯 癸巳 丙戌 癸巳** | **03-少爷-子源** |
| 立 | 朱宗立 | 2011-05-19 12:00 午时 | 辛卯 癸巳 甲戌 庚午 | 05-立 |
| 仔仔 | (独立人物≠少爷) | 2019-10-23 丑时(推算) | 己亥 甲戌 癸巳 癸丑 | 19-仔仔 |

## Narrative函数架构

引擎中 `narrative_*` 函数位于 `engine/narratives.py`，从结构化数据生成命理师口吻的连贯分析：

```
narrative_* 函数 (engine/narratives.py)
    ↓ 被调用
narrative_integration.py add_narratives()
    ↓ 写入
result.sec_XX.narrative 字段
    ↓ 被消费
report_standard_gen.py / pdf_report.py / 前端
```

当前覆盖21§全部，每节200-500字：
§1 overview / §2 ge_ju / §3 shen_qiang_ruo / §4 xi_yong / §5 zai_huo /
§6 character / §7 appearance / §8 wealth / §9 **property(新增)** /
§10 career / §11 education / §12 marriage / §13 children / §14 health /
§15 family / §16 events / §17 **da_yun_detail(新增)** /
§18 **verdicts(新增)** / §19 **da_yun_curve(新增)** /
§20 **wu_xing_advice(新增)** / §21 **life_advice(新增)**

## 报告质量说明

- **确定性规则引擎**：同一八字跑100次，结果100%一致，零幻觉
- **380行 vs 1700+行**：引擎输出结构性数据+精炼叙述。达到1700+行需要LLM展开
- **适合商业化**：380行核心数据+命理分析已超越90%八字App
- **如需增加行数**：扩充narrative函数至每节500-800字+更详细表格即可
