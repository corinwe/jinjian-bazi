# Chroma知识库向量化陷阱与修复（2026-07-29）

> 场景：五经典吸收时重建向量库（220块→635块），踩了2个静默bug。
> 核心教训：向量库"入库成功"≠"检索命中"。入库后必须用真实查询验证检索结果。

## 陷阱1：section白名单过滤导致新知识永不命中

`pre_retrieval_hook.py` 用 `where={"section": {"$in": required}}` 过滤检索。
- 初始白名单只有 `['§37','§38','§35']` 等技能章节
- 经典文档入库时标记为 `经典-穷通宝鉴` 等 → **永远被过滤掉**，检索结果全是§37
- 症状：知识块数量对（count=635），但查"甲木体象"返回的还是旧§37块

**修复**：`get_required_sections()` 各任务类型白名单加入经典前缀：
```python
'通用': ['§37','§38','§35','经典-穷通宝鉴','经典-滴天髓','经典-子平真诠','经典-三命通会','经典-渊海子平'],
```
**规则**：每次新增知识类型（新section前缀），必须同步更新白名单，并跑一次检索验证。

## 陷阱2：文件名拼音导致中文书名识别失败

`chunk_by_sections()` 最初用中文书名匹配文件名：
```python
if key in os.path.basename(source_path)  # '穷通宝鉴' in 'classic_qiongtongbaojian_20260729.md' → False!
```
文件名是拼音（qiongtongbaojian），中文key永远匹配不上 → 所有块fallback成 `§37`。
症状：入库后经典块分布显示 `经典-渊海子平: 3块`（只有标题含书名的3块对），其余167块全标成§37。

**修复**：显式拼音→中文映射：
```python
pinyin_map = {'qiongtongbaojian': '经典-穷通宝鉴', 'ditiansui': '经典-滴天髓',
              'zipingzhenquan': '经典-子平真诠', 'sanmingtonghui': '经典-三命通会',
              'yuanhaiziping': '经典-渊海子平'}
```
**规则**：文件名用拼音时，section提取必须用映射表，不能依赖中文子串匹配。

## 陷阱3：经典文档标题不含书名（逐标题判断失败）

即便有中文书名，经典文档内部标题是"§1 论月令定格""一、通神论"等，不含书名。
**修复**：source_type=="classic" 时，section前缀由文件名映射一次决定，整个文件统一用该前缀，不逐标题判断。

## 建库与验证流程（正确做法）

```bash
# 1. 建库/重建
python3 architecture/index_knowledge.py   # 删除旧collection重建，逐文件打印块数

# 2. 验证分布（确认新section真的标对了）
python3 -c "
import chromadb
col = chromadb.PersistentClient(path='.../chroma_db').get_collection('jinjian-bazi-knowledge')
data = col.get(limit=700, include=['metadatas'])
from collections import Counter
print(Counter(m['section'] for m in data['metadatas']))
"

# 3. 检索命中验证（确认白名单放行）
from pre_retrieval_hook import PreRetrievalHook
kb, refs = hook.retrieve('甲木 体象 参天大树', '通用')
# 期望：refs中出现 经典-滴天髓/经典-穷通宝鉴 等
```

## 当前知识库构成（2026-07-31·五经典全文+盲派全量）

| 来源 | 块数 | section标记 |
|:-----|:----:|:------------|
| SKILL.md 主文件 | 266 | §37等 |
| 渊海子平（精读+全文12卷+全文302章评注） | 485 | 经典-渊海子平 |
| 三命通会（精读+全文384章） | 432 | 经典-三命通会 |
| 滴天髓（精读+全文64篇） | 116 | 经典-滴天髓 |
| 子平真诠（精读+全文48章徐注） | 91 | 经典-子平真诠 |
| 穷通宝鉴（精读+全文11篇） | 34 | 经典-穷通宝鉴 |
| 杨清娟盲派（框架+食伤做功） | 66 | 经典-杨清娟盲派 |
| 段建业盲派（核心提取+初级命理学全文） | 30 | 经典-段建业盲派 |
| 盲派做功/寻根基 | 29 | 经典-盲派做功/寻根基 |
| ziping-theory-schools 方法论 | 21 | §37 |
| report_template_21s SOP | 19 | §37 |
| **总计** | **1589** | |

**新模式**：同一经典的"精读版+全文版"并存——全文按章切块（如三命通会每章一个知识块），精读版提供速查要点，二者共用同一 section 前缀（如`经典-三命通会`），检索时合并参与排名。

## 检索深度
TOP_K 从5提到8（经典块与§37块竞争，5太浅经典常被挤出）。
再补：全文版入库后，用"原文风格查询"验证（如"六辛日壬辰时 伤官伤尽"应命中经典-三命通会），现代白话查询对古文命中率天然偏低（DefaultEmbeddingFunction对中文古文支持有限），属已知限制，不误判为入库失败。
