# liu_nian_v2.py 2026-07-05 修复报告（5规则同时落地）

> 修复清单：R25宫位断事 + R30断语四要素 + R31分时段 + R35干透干藏 + R36五行类象
> 修复时间：2026-07-05
> 修复责任人：金鉴真人·Hermes Agent

---

## 修复概览

| 规则 | 规则名 | 修复类型 | 核心代码 | 状态 |
|:----|:-------|:--------|:---------|:----:|
| R25 | 宫位·身体·六亲对应体系 | 新增 | `GONG_WEI_MAP` + `_find_pillar_interactions()` | ✅ |
| R30 | 断语四要素格式 | 新增 | `_build_event_desc()` + `_build_degree_str()` | ✅ |
| R31 | 分时段断事（上半年/下半年） | 新增 | 全年+上半年(天干70%)+下半年(地支70%)三事件 | ✅ |
| R35 | 干透干藏应事规则（比劫主动/被动） | 新增 | `_get_bi_jie_desc()` | ✅ |
| R36 | 地支五行类象逢冲应事 | 新增 | `CHONG_WU_XING_LEI_XIANG` + `_get_chong_lei_xiang()` | ✅ |

**额外修复（子Agent冲突后补）：**
| R39 | 恶神能量级别对应表 | 补全常量 | `E_SHEN_LEVEL` dict | ✅ |
| R40 | 神煞 vs 十神系统界限 | 补全常量 | `SHEN_SHA_BOUNDARY_NOTE` | ✅ |

---

## R25 — 宫位·身体·六亲对应体系

### 新增数据结构

```python
GONG_WEI_MAP = {
    0: {"六亲": "祖上/父母", "身体": "头部/大脑/眼睛"},
    1: {"六亲": "父母/兄弟姐妹", "身体": "胸部/肩颈/心肺"},
    2: {"六亲": "配偶/自身", "身体": "腹部/腰肾/生殖"},
    3: {"六亲": "子女/下属", "身体": "腿部/足部/关节"},
}
```

### 新增函数

- `_get_gong_wei_info(pillar_idx)` — 根据柱序号返回宫位描述字符串
- `_find_pillar_interactions(liu_nian_zhi, all_zhis)` — 检测流年地支与四柱的冲/合/刑/害/破关系

### 效果

之前：`💰 发财窗口: 财星流年`
之后：`[全年]，💰 发财，配偶·腹部（财星引动），（程度：重大）`

事件描述中少了"哪位六亲应事"的模糊性 → 有了具体的身体部位和六亲指向。

---

## R30 — 断语四要素格式

### 新增函数

```python
def _build_degree_str(confidence: float) -> str:
    if confidence >= 0.8: return "（程度：重大）"
    elif confidence >= 0.6: return "（程度：显著）"
    elif confidence >= 0.5: return "（程度：一般）"
    return "（程度：轻微）"

def _build_event_desc(event_type, base_desc, gong_wei_str="", 
                      chong_lei_xiang="", bi_jie_str="", period="", confidence=0.0):
    # 格式: [时段]，标签，宫位：描述：五行类象：（程度：xx）
```

### 效果

所有8种事件类型（发财/灾祸/结婚/职业/学业/健康/搬迁/添丁）都使用 `_build_event_desc()` 格式输出，满足 skill §12.0 要点④要求。

---

## R31 — 分时段断事（上半年/下半年）

### 核心逻辑

每一年产生 **3 × N** 个事件描述（N为检测到的事件类型数）：
- **全年事件**（原始置信度）— 原始完整描述
- **上半年事件**（置信度×0.7+0.1）— `[上半年·天干主导70%]` 前缀 + 应期：1-6月
- **下半年事件**（置信度×0.7+0.1）— `[下半年·地支主导70%]` 前缀 + 应期：7-12月

### 实现细节

上半年和下半年的描述从原始全年事件提取事件标签和核心内容，不嵌套已有格式。提取逻辑：

1. 去掉 `[全年]` 前缀
2. 通过emoji（💰/⚠️/💍/💼/📚/🏥）找到事件标签
3. 从标签之后截取到第一个 `（程度` 之前的内容作为核心描述
4. 用 `_build_degree_str()` 重新生成程度词
5. 附加应期信息

### 调用方兼容

`extract_key_events()` 仍按 `confidence >= 0.5` 筛选，上半年/下半年事件因置信度较低可能被过滤。`events` 列表中同时包含全年/上半年/下半年三条记录。

---

## R35 — 干透干藏应事规则

### 新增函数

```python
def _get_bi_jie_desc(liu_nian_shi_shen, shen_label):
    if liu_nian_shi_shen not in ["比肩", "劫财"]:
        return ""
    if shen_label == "身强":
        return "他人劫夺/竞争失利，注意财物安全"
    else:
        return "朋友帮身/合作顺利，利社交"
```

### 效果

当流年天干为比肩/劫财时，事件描述中自动追加干透干藏的主动/被动区分。非比劫流年返回空字符串，不影响其他事件。

---

## R36 — 地支五行类象逢冲应事

### 新增常量

```python
YI_MA_ZHI = {"寅", "申", "巳", "亥"}
TAO_HUA_ZHI = {"子", "午", "卯", "酉"}
TU_ZHI = {"辰", "戌", "丑", "未"}

CHONG_WU_XING_LEI_XIANG = {
    "土": "住宅变动/房地产变化/搬迁",
    "驿马": "职业变化/工作调动/远行",
    "桃花": "权力变化/地位变动/情感纠纷",
}
```

### 新增函数

```python
def _get_chong_lei_xiang(liu_nian_zhi, other_zhi):
    # 土冲（辰戌/丑未）→ 住宅变动
    # 驿马冲（寅申巳亥）→ 职业变化
    # 桃花冲（子午卯酉）→ 权力变化
```

### 效果

当流年地支与四柱地支存在六冲关系时，自动判断冲的五行类象，追加到事件描述中。

---

## 🚨 子Agent冲突 Pitfall

**发现场景**：两个 subagent 同时修改 `liu_nian_v2.py` — 一个添加了R39/R40代码（引用了`E_SHEN_LEVEL`和`SHEN_SHA_BOUNDARY_NOTE`），但未添加常量定义，导致 NameError。

**修复方法**：在 `CHONG_WU_XING_LEI_XIANG` 后追加常量定义：

```python
E_SHEN_LEVEL = {
    "七杀": {20: "横死猝死(20倍)", 10: "重病手术(10倍)", 7: "官非牢狱(7倍)", 3: "压力/罚单(3倍)", 1: "小麻烦(1倍)"},
    "伤官": {10: "官非破财(10倍)", 7: "口舌是非(7倍)", 3: "言语冲突(3倍)", 1: "不满情绪(1倍)"},
    "枭印": {10: "精神异常(10倍)", 7: "思维混乱(7倍)", 3: "焦虑多疑(3倍)", 1: "灵感波动(1倍)"},
    "劫财": {10: "破财破产(10倍)", 7: "合作破裂(7倍)", 3: "小破财(3倍)", 1: "应酬多(1倍)"},
}
SHEN_SHA_BOUNDARY_NOTE = "（天乙贵人不能解十神系统恶神，仅解神煞系统）"
```

**铁律**：子Agent并行修改同一文件时，修改后必须做一次 **全文件错误扫描**（`python3 -c "from liu_nian_v2 import ..."`），确认无 NameError / ImportError。子Agent之间无法感知彼此的修改，唯一的安全网就是 import 测试。

---

## 测试验证结果

- `from liu_nian_v2 import analyze_liu_nian_range` ✅ 
- `test_full_suite.py`: **347/361 PASS (96.1%)** 
- 14个FAIL均为预存问题（大运步数8→11、F3文昌格式、G2 summary字段），与本次修改无关

---

## 2026-07-05 二修：R32+R33+R34+R37+R29（5规则再次落地）

> 修复清单：R32流年合宫位应事 + R33流年逢冲应事 + R34流年来害应事 + R37运年合绊相冲5条规律 + R29过三关断事
> 修复时间：2026-07-05（会话二）
> 修复责任人：金鉴真人·Hermes Agent

### 修复概览

| 规则 | 规则名 | 修复类型 | 核心代码 | 状态 |
|:----|:-------|:--------|:---------|:----:|
| R32 | 流年合各宫位应事 | 新增 | `_get_he_ying_shi(pillar_idx)` | ✅ |
| R33 | 流年逢冲各宫位应事 | 新增 | `_get_chong_ying_shi(ln_zhi, other_zhi, p_idx)` | ✅ |
| R34 | 流年来害各宫位应事 | 新增 | `_get_hai_ying_shi(pillar_idx)` | ✅ |
| R37 | 运年合绊相冲5条规律 | 新增 | `_get_yun_nian_he_ban_tiao_lv(...)` | ✅ |
| R29 | 过三关断事方法 | 新增 | `apply_three_guan_filter(events)` | ✅ |

### R32 — 流年合各宫位应事

规则（来源：公众号文章②·八字断流年技巧）：合年宫→长辈身体欠安，合月令→心情郁闷，合夫妻宫→结婚或离婚，合时柱→怀胎或子女事。

```python
def _get_he_ying_shi(pillar_idx: int) -> str:
    MAP = {0: "长辈身体欠安", 1: "心情郁闷", 2: "结婚或离婚", 3: "怀胎或子女事"}
    return MAP.get(pillar_idx, "")
```

集成：从 `pillar_interactions` 的「合」列表遍历，产生 `【合】xxx` 格式，合并到 `ying_shi` 字段。

### R33 — 流年逢冲各宫位应事

规则：冲库→库被冲开，冲驿马(寅申巳亥)→职业变动/搬迁，冲桃花(子午卯酉)→情感困扰，冲年→隐忍莫争执，冲月→动心起念，冲日→婚姻变动，冲时→怀胎/子女事。

与R36的区分：R36按五行类别分类（土→住宅、驿马→职业、桃花→权力），R33按宫位分类。两者同时存在、输出到不同字段（R36→`chong_lei_xiang_str`，R33→`ying_shi_combined`）。

### R34 — 流年来害各宫位应事

规则：害年宫→与长辈分开，害月柱→整年心情郁闷，害夫妻宫→聚少离多，害时柱→与子女分开。

### R37 — 运年合绊相冲5条规律

| 序号 | 规则 | 标签 | 触发条件 |
|:---:|:----|:----|:---------|
| ① | 以绊论吉凶 | 【合绊】 | 大运与流年有合/冲关系 |
| ② | 实神被作用 | 【实神】 | 流年地支与原局任一柱有合/冲 |
| ③ | 干支一气力大 | 【一气】 | 流年天干地支五行相同 |
| ④ | 绊住后仍可作用 | 【余气】 | 有合绊关系时 |
| ⑤ | 虚神看喜忌 | 【虚神】 | 流年字不在原局中 |

输出格式：`【合绊】xxx | 【实神】xxx | 【一气】xxx`，存入 `he_ban` 字段。

### R29 — 过三关断事方法

```python
def apply_three_guan_filter(events: dict) -> dict:
    """每种事件类型只取置信度最高的3件事"""
    filtered = {}
    for etype, evts in events.items():
        if evts:
            sorted_evts = sorted(evts, key=lambda x: x.get("confidence", 0), reverse=True)
            filtered[etype] = sorted_evts[:3]
    return filtered
```

集成：`extract_key_events()` 在收集完所有事件后调用过滤。仅影响外部提取接口，`analyze_liu_nian_v2()` 内部 `events` 列表不受影响。

### 返回值新增字段

`analyze_liu_nian_v2()` 的 return dict 新增：
- `"ying_shi"` — R32-34应事描述，如 `"【合】结婚或离婚；【冲】库被冲开"`
- `"he_ban"` — R37合绊规律，如 `"【合绊】以绊论吉凶 | 【实神】大运/流年引动原局实神"`

### 测试验证（二修）

- 5个新函数单元测试全部通过（`_get_he_ying_shi`, `_get_chong_ying_shi`, `_get_hai_ying_shi`, `_get_yun_nian_he_ban_tiao_lv`, `apply_three_guan_filter`）
- 全量测试：**347/361 PASS (96.1%)**，14个FAIL均为预存问题，0回归
