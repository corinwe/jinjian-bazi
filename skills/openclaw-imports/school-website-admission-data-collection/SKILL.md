---
name: "school-website-admission-data-collection"
description: "如何从中国国际学校和公立学校国际部的官方网站上，系统性地收集近几年的大学升学录取数据。当用户提到需要收集学校升学数据、爬取官网录取信息、整理毕业生去向、制作国际学校录取报告、获取Top100国际高中榜单数据、或者需要紧急在几小时内完成大量学校数据收集时，都应触发此技能。关键词包括：升学数据、官网扒取、毕业生去向、录取报告、国际高中排名、数据收集脚本、紧急任务。"
metadata: { "openclaw": { "emoji": "🎓" } }
---

# 从学校官网收集升学数据

本技能指导你如何系统、高效地从中国国际学校和公立学校国际部的官方网站上，收集并结构化其近年的大学升学录取数据，尤其适用于时间紧迫的批量数据收集任务。

## 何时使用此技能
- 当你需要为中国Top100国际高中或公立学校国际部建立升学数据库时。
- 当用户要求从学校官网“扒取”近几年的毕业生去向、录取名单等权威数据时。
- 当任务时间紧迫（例如几小时内），需要制定并行化、自动化的数据收集策略时。

## 步骤
1.  **明确目标与创建计划**
    *   **做什么**：首先与用户确认数据范围（如“近5年”、“Top100学校”）、截止时间、以及所需数据字段（如大学名称、国家、专业、录取人数、奖学金）。
    *   **为什么**：清晰的目标是高效执行的基础，尤其是面对紧急任务时，必须优先确定范围和优先级。

2.  **建立标准化数据模板**
    *   **做什么**：创建一个结构化的JSON数据模板，以统一后续收集到的所有信息。模板应包含学校基本信息（名称、类型、地点、年份）和详细的录取数据列表。
    *   **为什么**：统一的数据格式是后续进行数据分析、报告生成和数据库导入的前提，能避免混乱。

3.  **整理目标学校名单**
    *   **做什么**：基于任务目标（如“中国Top100”），快速整理一份包含学校名称、类型、所在城市和官网URL的初始名单。可以按地区（北京、上海、广深等）分组。
    *   **为什么**：一份清晰的名单是执行路线图，便于分配任务、跟踪进度，并为自动化脚本提供输入源。

4.  **分阶段执行数据收集**
    *   **做什么**：将收集过程分为两个阶段：1) **基础信息收集**：快速验证名单中所有学校的官网可访问性，并记录基础信息。2) **详细数据挖掘**：针对官网结构清晰的学校，深入查找“升学指导”、“毕业生去向”、“年度录取报告”等页面。
    *   **为什么**：分阶段处理可以快速产出初步成果（完成名单），同时集中精力攻克有价值的数据源，最大化时间利用效率。

5.  **使用自动化脚本辅助**
    *   **做什么**：编写Python脚本（如 `collect_school_data.py`）来自动化部分流程，例如批量读取学校名单、模拟访问官网（使用如 `requests` 库）、搜索页面中的关键词（如“大学”、“offer”、“admission”）。
    *   **为什么**：对于大批量学校，自动化脚本可以极大地提高效率，快速筛选出含有升学信息关键词的网站，为人工深度挖掘提供目标。

6.  **人工访问与数据提取**
    *   **做什么**：对于脚本筛选出的或已知的重点学校，使用浏览器进行人工访问。在官网中寻找导航菜单（如“Admissions”、“Guidance”、“About”），并使用站内搜索功能查找“college admissions”、“university acceptance”等关键词。
    *   **为什么**：许多学校官网使用JavaScript动态加载内容，自动化工具可能无法直接获取。人工访问可以处理复杂的页面交互，并准确找到数据所在的文章或报告链接。

7.  **数据整理与报告生成**
    *   **做什么**：将收集到的原始数据（可能是网页文本、PDF内容或列表）清洗、格式化，并填入步骤2创建的标准模板中。最后汇总所有学校数据，形成结构化报告（如JSON文件）或可视化图表。
    *   **为什么**：原始数据需要转化为可用的结构化信息，这是交付给用户的最终成果，也是导入数据库的直接输入。

## 陷阱与解决方案
- ❌ **陷阱**：试图用一个完全自动化的工具一次性抓取所有学校的详细数据。
  *   **原因**：各学校官网技术栈（如JavaScript框架）、页面结构差异巨大，完全自动化成功率低，且容易被反爬机制阻挡。
  *   ✅ **解决方案**：采用“自动化筛选 + 人工精挖”的组合策略。用脚本快速扫描大量网站，定位潜在的数据页面；再由人工对重点目标进行访问和数据提取。

- ❌ **陷阱**：在单个学校的官网上花费过多时间寻找数据。
  *   **原因**：有些学校的数据可能藏得很深，或需要登录才能访问，在时间紧迫的任务中这会拖慢整体进度。
  *   ✅ **解决方案**：为每个学校的调查设定时间上限（如10-15分钟）。如果找不到，先记录状态并跳过，优先收集那些数据公开、结构清晰的学校，确保在截止时间前获得尽可能多的有效数据。

- ❌ **陷阱**：只关注“毕业生去向”字样的页面。
  *   **原因**：不同学校对升学数据页面的命名不同，常见的有“College Admissions Review”、“University Counseling”、“录取喜报”、“School Profile”。
  *   ✅ **解决方案**：灵活使用多种关键词进行搜索，包括中英文。例如：“升学”、“录取”、“admission”、“acceptance”、“counseling”。关注学校的新闻公告或年度报告板块，数据常以新闻文章形式发布。

## 关键代码和配置
**标准化数据模板 (data_template.json):**
```json
{
  "school": "学校名称",
  "type": "国际学校/公办国际部/民办国际高中",
  "location": "城市",
  "year": 2025,
  "total_graduates": 毕业生总数,
  "offer_data": [
    {
      "university": "大学名称",
      "country": "国家",
      "major": "专业",
      "count": 录取人数,
      "scholarship": "奖学金信息"
    }
  ]
}
```

**自动化数据收集脚本示例 (collect_school_data.py 核心部分):**
```python
import json
import requests
from bs4 import BeautifulSoup

# 学校名单
schools = [
    {"name": "北京顺义国际学校", "url": "https://www.isb.bj.edu.cn", "type": "国际学校", "location": "北京"},
    {"name": "上海中学国际部", "url": "https://www.shsid.org", "type": "公办国际部", "location": "上海"},
    # ... 更多学校
]

def collect_school_info(schools):
    results = []
    for school in schools:
        try:
            # 尝试访问官网
            response = requests.get(school['url'], timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text().lower()
            
            # 检查是否包含升学相关关键词
            keywords = ['大学', '录取', 'offer', 'admission', 'college', 'university', '升学', '毕业生']
            found_keywords = [kw for kw in keywords if kw in text]
            
            school_data = {
                "school": school['name'],
                "type": school['type'],
                "location": school['location'],
                "website": school['url'],
                "status": "可访问",
                "found_keywords": found_keywords
            }
            results.append(school_data)
            
        except Exception as e:
            # 记录访问失败的学校
            results.append({
                "school": school['name'],
                "type": school['type'],
                "location": school['location'],
                "website": school['url'],
                "status": f"访问失败: {str(e)}",
                "found_keywords": []
            })
    
    # 保存结果
    with open('schools_basic_info.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results
```

## 环境与先决条件
- **编程环境**：Python 3.x，并安装 `requests`, `beautifulsoup4` 库用于网页抓取和分析。
- **网络**：能够访问中国大陆境内外网站（部分国际学校官网可能托管在海外）。
- **工具**：一个现代化的浏览器（如Chrome, Edge）用于人工访问和调试。
- **技能**：基础的Python编程能力和网页HTML结构知识。

## 配套文件
- `scripts/collect_school_data.py` - 用于批量检查学校官网可访问性并搜索关键词的自动化脚本。
- `references/top100_international_schools_list.md` - 中国Top100国际高中及公立学校国际部的参考名单（需根据最新资料更新）。

## Companion files

- `scripts/collect_school_data.py` — automation script
- `scripts/create_data_template.py` — automation script
- `scripts/generate_schools_list.py` — automation script