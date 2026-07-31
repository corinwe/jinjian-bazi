# 公版古籍全文批量抓取（gushiwen.cn）· 2026-07-31 三命通会实战

> 结果：三命通会 384章 / 326,384字 / 966KB 全文抓取成功 → 知识库+技能库+Chroma(385块) 三落点。
> 适用于：渊海子平/滴天髓/子平真诠等公版古籍的全文补全。

## 1. 来源对比结论

| 来源 | 质量 | 覆盖 | 结论 |
|:-----|:-----|:-----|:-----|
| ctext.org | 最高（四库全书本） | ⚠️ 部分卷（三命通会仅9/12卷） | 质量对照用 |
| **gushiwen.cn（m.移动版）** | 好 | ✅ 完整（单页全索引） | **首选** |
| httpcn.com | — | ❌ 302重定向首页（JS渲染） | 弃 |
| 8bei8.com | — | ⚠️ 需浏览器 | 备选 |

## 2. 索引页提取（关键：单页含全部章节）

```python
import re, html, urllib.request

INDEX_URL = "https://m.gushiwen.cn/guwen/book_1fe1780cd61a.aspx"  # 三命通会
req = urllib.request.Request(INDEX_URL, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)'})
content = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='ignore')

links = re.findall(r'<a[^>]*href="(/guwen/bookv_[a-z0-9]+\.aspx)"[^>]*>([^<]*)</a>', content)
# 实测 384 个章节链接（无分页！一次拿全）
```

**注意**：gushiwen 章节索引**不分页**（384章全在1页），不要找页码。书hash在URL `book_{hash}.aspx`，章节hash是 `bookv_{hash}.aspx`。

## 3. 章节正文提取

```python
def fetch(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode('utf-8', errors='ignore')
        except Exception:
            import time; time.sleep(2)
    raise RuntimeError(url)

page = fetch(f"https://m.gushiwen.cn{href}")
m = re.search(r'<div class="contson"[^>]*>(.*?)</div>', page, flags=re.S)
body = m.group(1) if m else ''
body = re.sub(r'<br[^>]*>', '\n', body)
body = re.sub(r'<[^>]+>', '', body)
body = html.unescape(body)
body = re.sub(r'[ \t]+', ' ', body)
body = re.sub(r'\n\s*\n+', '\n', body).strip()
```

**关键参数**：每章间隔 `time.sleep(0.5)`（防反爬）；顺序执行不并发；失败记录不中断；每20章打印进度。

## 4. 合并+向量化

```python
# 合并全文：每章写成 "## 第N章 标题\n\n{body}\n"
# → 966KB md → 直接给 index_knowledge.py 按 ## 切块 → 385块
```

## 5. 结构识别（三命通会）

```
第1-184章  理论篇（原造化之始/五行/纳音/六十甲子/十神/神煞/大运流年）
第185-304章 六X日X时断×120章（六甲日甲子→六癸日癸亥·逐日断命核心·实战价值最高）
第305-384章 其余断命章（印绶/伤官/食神/财/官/杀/招嫁不定...）
```

## 6. 向量化后验证

```python
# pre_retrieval_hook 白名单须含 '经典-三命通会'（全文与精要共用同一 section 前缀）
# 检索实测：
#   "六辛日壬辰时 伤官伤尽" → 命中 经典-三命通会
#   "六甲日甲子时 富贵"     → 命中 经典-三命通会
# Chroma count 748 → 1133（三命通会全文385块）
```

## 7. 与精要版的关系

- 精要版 `classic_sanmingtonghui_20260729.md`（34KB）= 结构化要点，供快速参考
- 全文版 `三命通会_全文12卷_384章_20260731.md`（966KB）= 深度参考，逐章可查
- 两者并存：全文按章向量化（每章一块），检索可精确命中到具体断章
