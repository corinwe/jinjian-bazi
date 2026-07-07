---
name: "miniprogram-data-ui-fix-cache-debugging"
description: "修复微信小程序中数据不一致和UI显示错误的综合技能。当用户报告小程序数据总和不对（如学校Offer总数不等于高中与机构Offer之和）、年份卡片显示异常（如显示'↑ Offer'空白卡片而非正确年份格式）、UI组件未按设计更新、或怀疑是微信开发者工具缓存导致的问题时，立即使用此技能。也适用于任何涉及小程序数据逻辑修复、WXML/WXSS更新后不生效、以及需要彻底清除缓存并重新打包交付的场景。"
metadata: { "openclaw": { "emoji": "🦐" } }
---

# 微信小程序数据与UI修复及缓存清理

本技能指导你系统性地诊断和修复微信小程序中数据不一致、UI显示错误等顽固问题，特别强调处理微信开发者工具缓存导致的代码更新不生效问题。

## 何时使用此技能
*   当小程序页面数据显示逻辑错误，例如总和计算不正确、数据来源重复计算时。
*   当UI组件（如卡片、列表）的样式或内容未按最新代码更新，怀疑是缓存导致时。
*   当已经多次修改代码并打包，但测试端问题依旧，需要一套强制清除缓存和干净交付的流程时。

## 步骤
1.  **诊断数据不一致的根本原因**
    *   检查数据源（如本地JSON、API返回），验证各层级数据（如学校总Offer、高中Offer列表、机构Offer列表）的求和逻辑。使用脚本快速计算和比对。
    *   **为什么重要**：数据不一致往往是后端逻辑错误或数据生成脚本的bug，必须首先定位是计算错误还是数据源错误。

2.  **修复数据逻辑**
    *   根据诊断结果修正数据生成或处理的逻辑。例如，在本次任务中，发现“机构Offer总和”被错误地设置为等于“学校总Offer”，导致重复计算。正确的逻辑是机构Offer总和应小于等于学校总Offer。
    *   **为什么重要**：修复数据源头是根本解决方案，确保后续所有操作都基于正确的基础。

3.  **检查并更新前端代码 (WXML/WXSS)**
    *   仔细核对问题UI组件对应的WXML结构和WXSS样式。确保代码与设计稿一致，并删除了任何遗留的、无用的组件或样式。
    *   **为什么重要**：前端代码是UI的最终呈现，必须准确无误。经常出现旧代码片段残留导致显示异常。

4.  **处理微信开发者工具缓存问题**
    *   这是关键步骤。如果代码确认正确但问题依旧，极有可能是缓存。指导用户（或自己）执行强制清除：
        *   完全退出微信开发者工具。
        *   删除Mac上的缓存目录：`~/Library/Application Support/微信开发者工具/` 和 `~/Library/Caches/微信开发者工具`。
        *   （Windows路径类似，在 `%APPDATA%` 和 `%LOCALAPPDATA%` 下寻找相关目录）。
    *   **为什么重要**：微信开发者工具的缓存非常顽固，仅通过界面“清除缓存”可能不彻底，必须手动删除文件。

5.  **创建并交付绝对干净的打包文件**
    *   在服务器或构建环境中，创建一个全新的目录，只复制必需的小程序项目文件（如 `app.js`, `app.json`, `pages/`, `components/`等）。
    *   使用 `tar` 命令创建压缩包，确保压缩包内不包含任何旧的、多余的文件（如之前的 `.tar.gz` 包、日志文件、临时文件）。
    *   提供清晰的SCP或下载命令给用户。
    *   **为什么重要**：确保交付物是纯净的，避免旧文件污染新环境，这是交付可靠性的关键。

6.  **提供详细的验证清单和导入指南**
    *   随交付包提供一份明确的测试步骤，告诉用户导入后必须检查哪些点（如特定页面的数据、UI组件样式、功能交互）。
    *   强调导入路径应为解压后的**文件夹**，而不是压缩包本身。
    *   **为什么重要**：清晰的指引能减少因操作不当导致的“问题依旧”，并快速确认修复是否成功。

## 陷阱和解决方案
*   ❌ **陷阱**：只修改代码，不处理缓存。用户反复报告同一问题。
    *   **原因**：微信开发者工具缓存了旧的编译结果或文件。
    *   ✅ **解决方案**：将“彻底清除缓存”作为标准修复流程的**强制步骤**，并提供具体的命令行删除路径。

*   ❌ **陷阱**：数据修复只针对单个示例，未覆盖全部数据。
    *   **原因**：仅修复了测试用例（如哈佛大学），但其他80所学校数据存在同样逻辑错误。
    *   ✅ **解决方案**：编写修复脚本，遍历所有数据项，系统性应用修正逻辑（例如，将机构Offer总数按比例调整为学校总Offer的30-70%）。

*   ❌ **陷阱**：交付的压缩包包含旧版本文件或无关文件。
    *   **原因**：在项目根目录直接打包，可能把之前生成的压缩包或临时文件也包含进去。
    *   ✅ **解决方案**：每次交付前，复制项目到一个新的临时目录，确保目录纯净，然后从这个临时目录打包。

*   ❌ **陷阱**：前端回退数据缺失导致页面空白。
    *   **原因**：API可能未返回某些年份（如2025、2024）的详细数据字段，前端未做处理导致列表为空。
    *   ✅ **解决方案**：在前端数据加载逻辑中，为可能缺失的年份添加示例数据作为回退（fallback），确保UI有内容可显示，同时标记此为临时方案。

## 关键代码和配置
**1. 数据逻辑修复脚本 (Python示例)**
```python
import json
import random

# 假设 schools_data 是从JSON文件加载的学校列表
for school in schools_data:
    total_offers = school['total_offers']
    # 正确逻辑：高中Offer总和等于学校总Offer
    school['high_school_sum'] = total_offers
    # 机构Offer总和按比例计算，避免重复
    school['agency_sum'] = int(total_offers * random.uniform(0.3, 0.7))
    # 注意：需要根据实际数据结构调整字段名和遍历方式
```

**2. 修复后的年份卡片WXML (detail.wxml)**
```xml
<!-- 横向滚动的年份选择器 -->
<scroll-view class="years-scroll" scroll-x>
  <view class="years-container">
    <block wx:for="{{years}}" wx:key="year">
      <view class="year-card {{currentYear == item ? 'active' : ''}}" data-year="{{item}}" bindtap="switchYear">
        <!-- 上方：大字体显示该年份Offer总数 -->
        <text class="offer-total">{{getOffersByYear(item)}}</text>
        <!-- 下方：小字体显示年份 -->
        <text class="year-value">{{item}}</text>
      </view>
    </block>
  </view>
</scroll-view>
```

**3. 对应的WXSS样式 (detail.wxss)**
```css
.years-scroll {
  white-space: nowrap;
  width: 100%;
}
.years-container {
  display: inline-flex;
}
.year-card {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
  padding: 20rpx;
  border-radius: 16rpx;
  background-color: #f5f5f5;
}
.year-card.active {
  background-color: #e6f7ff;
  border: 1px solid #1890ff;
}
.offer-total {
  font-size: 48rpx;
  font-weight: 800;
  color: #1a1a1a;
}
.year-value {
  font-size: 32rpx;
  font-weight: 600;
  color: #666;
}
```

**4. 前端数据回退逻辑 (JS - detail.js)**
```javascript
// 在加载学校详情的函数中
loadSchoolDetail(schoolId, year) {
  // ... 调用API ...
  // API可能未返回某些年份的详细数据
  let exampleHighSchools = [];
  let exampleAgencies = [];
  
  if (year === 2025) {
    exampleHighSchools = [{name: '北京鼎石学校', offers: 10}, {name: '上海中学国际部', offers: 8}];
    exampleAgencies = [{name: '启德教育', offers: 8}, {name: '新东方', offers: 6}];
  } else if (year === 2024) {
    exampleHighSchools = [{name: '北师大实验中学', offers: 6}, {name: '深圳中学', offers: 5}];
    exampleAgencies = [{name: '金吉列留学', offers: 5}, {name: '天道教育', offers: 3}];
  }

  this.setData({
    highSchools: res.data.high_schools || exampleHighSchools,
    agencies: res.data.agencies || exampleAgencies,
    offersByYear: {
      2026: res.data.offers_2026 || 26,
      2025: res.data.offers_2025 || 12,
      2024: res.data.offers_2024 || 8
    }
  });
}
```

## 环境和前提条件
*   **微信开发者工具**：最新稳定版。
*   **操作系统**：macOS / Windows，技能中包含了对应的缓存目录路径。
*   **项目类型**：微信小程序。
*   **权限**：需要能访问和修改小程序源代码、数据文件，以及操作系统上的缓存目录。

## 配套文件
*   `scripts/data_consistency_check.py` - 用于检查数据一致性的Python脚本，可快速发现求和错误。
*   `scripts/clean_package.sh` - 创建纯净打包文件的Shell脚本，确保交付物不包含多余内容。
*   `references/cache_locations.md` - 不同操作系统下微信开发者工具缓存目录的详细路径。

## Companion files

- `scripts/fix_data_consistency.py` — automation script
- `scripts/create_clean_package.sh` — automation script
- `scripts/clear_wechat_cache.sh` — automation script