---
name: financial-research-assistant
description: >-
  Configure and operate as a specialized financial/wealth management assistant
  focused on tech sector investing. Covers persona setup (name, identity),
  daily learning + morning briefing cron jobs (Feishu/Lark/GitHub delivery),
  morning briefing execution (holdings tracking, data collection, report
  generation, GitHub Pages deployment), memory hygiene for multi-role
  switching, portfolio analysis workflows, A-share data APIs (Tencent/East
  Money), and model fallback configuration.
core_capabilities:
  - "Daily market/tech learning pipeline with cron-delivered briefings"
  - "Multi-market coverage: US stocks (NASDAQ/NYSE), A-shares, HK stocks"
  - "AI full-industry-chain analysis (chip → infra → model → application)"
  - "Investment portfolio management and wealth preservation strategy"
  - "Morning briefing execution: 3-tier holdings tracking, parallel data collection (Tencent API for A-shares, Google Finance for HK/US), report generation, GitHub Pages deployment with build.py"
  - "Feishu/Lark or GitHub as delivery channel for scheduled reports"
when_to_use:
  - User asks you to act as a financial / wealth / investment assistant
  - User gives you a new name or role for investment management
  - User requests daily morning reports on tech/investment learning
  - User needs model config review (primary + fallback providers)
  - User switches between project roles (e.g., product dev → finance)
  - User asks about portfolio holdings, stock prices, or A-share data
  - User requests daily morning briefing setup or configuration changes
  - User reports GitHub Pages deployment issues or cron job failures
intended_audience: Hermes agents configured as personal wealth assistants
---

# Financial Research Assistant (财富投资助手)

## Overview

This skill configures Hermes Agent as a dedicated **financial and wealth management assistant** focused on technology sector investments across US, China A-share, and Hong Kong stock markets. The primary interface is Feishu/Lark for daily briefings.

## Key Workflows

### 1. Persona Activation

When user rebrands you (e.g., "now you're called 九九, my wealth assistant"):

1. Update `memory(target='user')` with the new role, name, and expectations
2. Clear old project-scoped memory entries that don't apply to the new role
3. Set `memory(target='memory')` with model config and daily report schedule
4. **Crucially**: Remove stale entries one-by-one with `memory(action='remove')` — the tool requires exact substring matching and cannot bulk delete

### 2. Daily Report Scheduling (Twice-Daily)

The report runs **twice per day** via cron jobs:

| Time | Name | Style | Data Freshness |
|:---:|:----|:-----|:--------------|
| 🕛 **12:00** | 九九财富午间快报 | Light (~800-1000 chars) | A-share morning session closed; HK morning session closing; US previous close |
| 🕗 **20:00** | 九九财富晚间复盘 | Full (~1200-1500 chars) | ALL markets closed; US pre-market available |

#### Noon (12:00) prompt key instructions:
- Title: `# 🌅 九九财富午间速递 | YYYY-MM-DD | 周三 | 午间版` (include weekday and 午间版 suffix)
- Subtitle: e.g., `*📌 新能源+机器人赛道专题 · A股分化创业板走强 · 港股全线回调*` (key theme + market characterization)
- Output file: `reports/YYYY-MM-DD-noon.md`
- Data: A-share morning session via Tencent API; HK via Google Finance; US from prior close
- Sections: 持仓追踪 → 各科技板块走势一览 → 当日行业洞察精简版 → 午间操作建议
- Character target: ~800-1000 chars
- **⚠️ Boss's explicit preference (2026-05-27):** The noon report MUST use 各科技板块走势一览 (tech sector overview table) instead of 上午盘异动速览, and MUST end with 💰 午间操作建议 with clear buy/hold/sell/reduce signals. Do NOT default to the generic 后市关注 section for noon.

#### Evening (20:00) prompt key instructions:
- Title: `# 🌅 九九财富晚间复盘 | YYYY-MM-DD | 周X`
- Output file: `reports/YYYY-MM-DD.md`
- Data: All markets closed — full daily data
- Full 5-section template per §5.4 below
- Character target: ~1200-1500 chars

#### GitHub Pages Delivery (both slots)

```bash
cd ~/wealth-invest-daily && git pull --rebase origin main
python3 build.py
git add -A
git commit -m "📈 九九财富报告 - YYYY-MM-DD"
git push origin main
```

Reference files: `references/wealth-invest-daily-deployment.md` (full deployment workflow)

### Delivery: GitHub (alternative, for script-based push)

When boss says "推送到GitHub" or "放到GitHub仓库":

**Setup:**
1. Install `gh` CLI: `apt-get install gh -y`
2. Authenticate: `echo "$TOKEN" | gh auth login --with-token`
3. Create repo: `gh repo create corinwe/jiujiu-daily --public --description "九九每日财富投资晨报"`
4. Clone: `git clone git@github.com:corinwe/jiujiu-daily.git ~/jiujiu-daily`

**Cron job config with script:**
```
schedule: "0 8 * * *"
deliver: origin          # no Feishu delivery — script handles output
script: push-to-github.sh  # post-processing script path
```

The cron job prompt produces the report Markdown, a **script** (running AFTER LLM output) writes it to `reports/YYYY-MM-DD.md`, runs `build.py` (TTS audio + static site), then git commit + push.

**Reference files for GitHub delivery:**
- `references/github-push-setup.md` — full setup guide, pitfalls (jiujiu-daily variant with build.py)
- `references/wealth-invest-daily-deployment.md` — simpler Markdown-only variant (no build.py, different repo name), includes inline write+push workflow for broken-script scenarios
- `references/google-finance-price-scraping-20260513.md` — Concrete price data from Google Finance scraping during 2026-05-13 session. Calibration dataset for detecting sub-agent price hallucination. Documents working/non-working Google Finance URL patterns, NVDA stock split details, and actionable rules for price verification.
- `references/google-finance-price-scraping-20260516.md` — Updated calibration dataset from 2026-05-16 session (May 15 Friday close). Full verified price table for all HK/US holdings + indices + A-shares via Tencent API.
- `references/nvda-earnings-verified-20260522.md` — Verified NVDA Q1 FY2027 earnings from Google Finance scrape. Documents sub-agent earnings hallucination (claimed $43.2B revenue vs actual $81.6B).
- `references/google-finance-price-scraping-20260525.md` — Calibration dataset from 2026-05-25 session (May 22 close). Documents worst sub-agent hallucination yet: Meituan 3690 claimed HKD 168.30 vs actual HKD 81.35 (107% error). Full verified price table for all HK/US holdings + A-shares via Tencent API. NVDA earnings display format reference.
- `references/google-finance-price-scraping-20260528.md` — Calibration dataset from 2026-05-28 session. Documents cron date mismatch (prompt said May 27 Wed, system was May 28 Thu). Full verified price table for all HK/US holdings + A-shares. Xiaomi detailed analysis notes. Tencent API urllib.request usage to avoid tirith pipe-to-interpreter scanner.
- `scripts/push-to-github.sh` — reusable push script template (jiujiu-daily variant)

### 3. Model Configuration Review

When user asks about model setup:

| Config | How to Check |
|--------|-------------|
| **Primary model** | `grep -E "^model" ~/.hermes/config.yaml` |
| **Fallback providers** | `grep -A5 "fallback_providers" ~/.hermes/config.yaml` |
| **Provider details** | `cat ~/.hermes/config.yaml \| grep -A3 "custom_providers"` |
| **Full config** | `cat ~/.hermes/config.yaml` |

**Common gaps to flag:**
- Missing fallback provider (primary goes down → agent goes silent)
- No `api_max_retries` tunable for rate limits
- Environment variables for alternative providers not set

### 4. Memory Hygiene for Role Switching

When switching from a prior project role (e.g., product dev assistant) to financial assistant:

1. Audit current memory with `memory(action='add', ...)` error output
2. Remove stale entries in **exact** character match chunks
3. Each `remove` call handles one entry — be prepared for many calls
4. After clearing, add consolidated entries:
   - `target='user'`: boss identity, role, subscription preference, timezone
   - `target='memory'`: agent name, model config, cron schedule, gap notes

## 5. Daily Report Execution (午间快报 + 晚间复盘)

This section covers the detailed execution for both daily reports. The noon report (12:00) is a lighter midday briefing using morning session data; the evening report (20:00) is the full daily recap after all markets close. Both follow the same 3-tier portfolio structure below.

### 5.1 Portfolio Holdings (3-Tier Structure)

The boss (九九) maintains a **3-tier portfolio structure** that every morning briefing must cover:

#### 🥇 Tier 1: Holdings Pool (持仓池) — P&L tracking + catalyst analysis
- **港股：** 阿里9988, 小米1810, 美团3690, 蔚来9866
- **美股：** MSFT, ECL
- **A股：** 美的000333, 比亚迪002594, 300ETF, AI智能ETF(sh515070)
- **Analysis focus:** P&L per stock, cost basis movement, catalysts, rebalancing suggestions

Full holdings with cost basis, multi-account breakdown, and historical reference data:
- `references/portfolio-multi-account-structure.md` — 3-account structure (Futu A, Futu B, A-share broker), verified OCR capture from 2026-05-13
- `references/stock-quotes-reference.md` — Historical price reference data with Google Finance URL patterns
- `references/google-finance-price-scraping-20260513.md` — Price scraping calibration dataset, NVDA split notes
- `references/google-finance-price-scraping-20260516.md` — Updated calibration dataset from 2026-05-16 session (May 15 Friday close)
- `references/google-finance-price-scraping-20260525.md` — Calibration dataset from 2026-05-25 session documenting worst hallucination yet (Meituan 107% error)
- `references/google-finance-price-scraping-20260528.md` — Calibration dataset from 2026-05-28 session. Documents cron date mismatch (prompt said May 27 Wed, system was May 28 Thu)

#### 🥈 Tier 2: Industry Deep-Dive Theme (行业深度主题) — replaces scattered watchlist rotation
**This is the boss's highest-value section. The earlier version was criticized as lacking depth.**

Daily rotation (200-400 words analysis, must include comparison, attribution, and actionable judgment):
| Day | Theme | Comparison Framework |
|:---:|:------|:--------------------|
| Mon | **AI Chip Landscape** | NVDA vs AVGO vs AMD — valuation, growth, market share |
| Tue | **AI Application Race** | MSFT(OpenAI) vs GOOGL(Gemini) vs AMZN(Anthropic) vs META(Llama) |
| Wed | **China NEV + Robotics** | BYD/赛力斯/CATL vs Tesla/NIO full-industry scan |
| Thu | **AI Infrastructure Chain** | Chip → optical module → liquid cooling → server, NVDA supply chain (see `references/ai-infrastructure-chain-analysis.md` for comparison framework + data points) |
| Fri | **Weekly Market Recap** | Top 5 weekly movers + top 3 catalysts next week + portfolio diagnosis |

**⚠️ CRITICAL: Cron prompt date vs system date mismatch.** The cron job prompt template hardcodes a date string (e.g., "今天是2026年5月27日周三"). **Do NOT trust this as the actual date.** The system clock may differ — the cron may fire on a different day than expected (e.g., prompt says Wednesday but system says Thursday). **ALWAYS run `date` first** to verify the actual system date. Then align:
- Report date = system date (not the hardcoded cron template date)
- Deep-dive theme = the theme for the actual day of the week (not what the cron template says)
- Data freshness: use system date to determine which markets have fresh data and which are stale
- Exception: if the cron template date was explicitly set by the boss for a future-dated report (unlikely), follow instructions

**⚠️ Report date vs data date (critical for Friday runs):** When the evening (20:00) report fires on Friday at 20:00 Beijing time, all markets have closed for the week — A-shares at 15:00, HK at 16:00, US (Thursday/prior close). The report should be **dated Friday** (the publication date) and use **Friday close data** for A-shares and HK, and Thursday close for US. However, if this is a US holiday week (e.g., US closed Friday), adjust per the US holiday note below. The subtitle should always clarify data dates (e.g., "基于5月21日收盘数据的一周复盘").

**⚠️ US holiday scenarios — mixed data freshness (critical):** The US market observes several holidays (Memorial Day last Monday in May, July 4th, Labor Day first Monday in September, Thanksgiving Thursday/Friday, etc.) when US markets close but A-share and sometimes HK markets trade normally. When this happens:

- **Next-day cron run (e.g., Tuesday after Memorial Day Monday):** US data is stale from Friday (3 days old). A-share data is fresh from Monday (1 day old). HK data status depends on the specific holiday — HK may also be closed on some dates.
- **Subtitle MUST explain the discrepancy** — e.g., "*基于5月22日（美/港）及5月25日收盘（A股）数据*" to signal to the boss why data freshness differs across markets.
- **Do NOT treat this like a weekend run** — A-share data IS fresh, so the report should highlight A-share movements while noting US/HK markets were closed.
- **Catalyst calendar adjustment:** Any catalysts originally scheduled for the US holiday (e.g., NVDA after-hours moves) are delayed to the next US trading day. Update the catalyst table accordingly.
- **Memorial Day pattern:** This recurs annually in late May. The A-share market on Monday will usually have a directional signal (positive/negative) that the US market will react to when it reopens Tuesday — note this cross-market dynamic in the report.
| Sat/Sun | **Weekend Recap + Week Ahead** | Review this week's key events + top 3 catalysts for coming Monday |

**Weekend/off-day handling:** Cron jobs fire at 12:00 and 20:00 every day including Saturday and Sunday when markets are closed. Both time slots use the same Friday-close data on weekends. The **evening (20:00)** report is the primary weekend report (since noon and evening would have near-identical data). **Distinguish between Saturday (first post-market day) and Sunday (second post-market day) — they need different formats when both run consecutively.**

#### Saturday: Full Weekly Market Recap (first weekend day)
When the Saturday cron fires, produce the full "Weekly Market Recap" (expanded Fri format) covering the complete prior week's market events, portfolio performance by market, and forward look at the coming week.

**Saturday report structure (verified 2026-05-17, 2026-05-23):** (see `references/weekend-recap-execution-20260517.md` for full session trace)
1. Title: "# 🌅 九九财富晨报 | YYYY-MM-DD | 周六\n*📌 周末特辑 · 本周全市场深度复盘 & 下周展望*\n*基于5月XX日（周五）收盘数据*"
2. Holdings table: same 3-market merged table but use "周度总览" heading label and add a "周涨跌幅" column alongside single-day change
3. Deep-dive: choose the prior week's Friday theme (Weekly Market Recap) — review Monday-Friday key events with weekly framing, attribution to specific data
4. 精选潜力标的: use 7-role framework for 2 stocks with catalysts in the COMING week (e.g., NVDA 5/20 earnings, 蔚来 5/21) — the forward-look section is more valuable than rehashing old news
5. Catalyst table: "下周催化剂" with dates for Monday-Friday of the coming week
6. Character count: 1600-2000 chars is acceptable, more content expected for weekly wrap

#### Sunday: Sunday Preview (second weekend day — after Saturday recap already ran)
When the Sunday cron fires and a Saturday report already covered the full week recap, do NOT rehash the same content. Produce a **"Sunday Preview"** focused on the coming week:

**Sunday report structure (verified 2026-05-24):** (see `references/sunday-preview-execution-20260524.md` for full session trace)
1. Title: `# 🌅 九九财富晨报 | YYYY-MM-DD | 周日\n*📌 明日开市 · 全周前瞻 — [2-3 key themes for the coming week]*\n*基于5月XX日（周五）收盘数据，本周焦点：[top 2 catalysts]*`
2. Holdings table: same data as Saturday but frame as "前瞻速览" (forward look), add extra weight to the next-week catalyst column (e.g. "⭐ **5/26 Q1财报 — 全周最大催化剂**")
3. Deep-dive restructured as "周度前瞻 — 未来一周的[number]条主线" (week-ahead themes). Use 4-6 numbered themes each with 2-4 sentences covering: catalyst event → impacted positions → scenario analysis. This is NOT a week-in-review; it's a forward-looking analytical piece.
4. 雷达池速览: same format, unchanged
5. 精选潜力标的: same 7-role framework, but prioritize stocks with catalysts in the COMING week rather than this-week review
6. Catalyst calendar: updated for the coming Mon-Fri, same table format
7. Character count: 2000-2500 chars is reasonable (more forward-looking analysis to cover)
8. ⚠️ **Do NOT re-use the Saturday title template** — the Sunday report should be clearly distinct from Saturday's weekly recap. No "周末特辑" or "周度复盘" labels if Saturday already used them.

#### 🥉 Tier 3: Radar Pool (雷达池) — quick scan, 1 line each daily
- **🇺🇸 US Radar:** NVDA (5/20 earnings), AVGO, AMD, GOOGL
- **🇭🇰 HK Radar:** 0700.Tencent, 9992.Pop Mart, 0981.SMIC
- **🇨🇳 A-Share Radar:** 300308.Zhongji Innolight, 300750.CATL, 601127.Serres

Full radar pool with tickers and coverage chain in `references/market-watchlist-full.md`.

### 5.2 Data Collection (Parallel via delegate_task)

Use `delegate_task` with up to **4 concurrent sub-agents** (requires `max_concurrent_children: 4` in config.yaml under `delegation:`):

**⚠️ Config prerequisite:** The default `max_concurrent_children` is 3. To run all 4 tasks in parallel, add or update in `~/.hermes/config.yaml`:
```yaml
delegation:
  max_concurrent_children: 4
```
**⚠️ MID-SESSION LIMITATION: Even after patching config.yaml with `max_concurrent_children: 4` via the `patch` tool, the system still enforces the old value from session startup.** The config is read once at process launch — patching mid-session has no effect on delegate_task limits. Workaround: split into two batches:
- **Batch 1** (3 concurrent): Tasks A (HK stocks), B (US stocks), C (A-shares)
- **Batch 2** (1 task): Task D (industry deep-dive research)
- On the next session launch (or restart), the updated config takes effect.
If this is not set, split into two batches (e.g., 3 HK+US+CN first, then D deep-dive second).

- **Task A:** HK stocks (holdings + radar) + Hang Seng indices
- **Task B:** US stocks (holdings + radar) + US index overnight
- **Task C:** A-share stocks (holdings + radar)
- **⭐ Task D:** Industry deep-dive theme research (the day's themed analysis, 200-400 words)

#### Data Source Priority

| Market | Preferred Source | Fallback | Reference |
|:-------|:-----------------|:---------|:----------|
| A-share | `qt.gtimg.cn` (Tencent API, fastest, no rate limit) | `push2delay.eastmoney.com` (East Money API) | `references/tencent-stock-api.md`, `references/east-money-api.md` |
| HK stocks | `browser_navigate` → Google Finance (`quote/{CODE}:HKG`) | — | `references/stock-quotes-reference.md` |
| US stocks | `browser_navigate` → Google Finance (`quote/{TICKER}:NASDAQ` or `:NYSE`) | web_search | `references/stock-quotes-reference.md` |
| News/dynamics | delegate_task + web_search | — | — |
| P&L calculation | `scripts/calc-pnl.py` | ad-hoc Python | `references/stock-quotes-reference.md` |

**A-share data (Tencent API, preferred):**
```bash
curl -s "https://qt.gtimg.cn/q=sz002594,sz000333"
# GBK encoding! Python: .read().decode('gbk')
# Fields: [3]=current, [4]=prev_close, [31]=change, [32]=change_pct
```
See `references/tencent-stock-api.md` for full field map and Python/bash parsers.

**WeChat MP article content extraction** (when boss shares a mp.weixin.qq.com link for research):
- `browser_navigate` often fails with captcha ("环境异常") — use `curl` + `BeautifulSoup` instead
- Download: `curl -s -L <url> -o /tmp/wx.html -A "Mozilla/5.0..."`
- Parse with BeautifulSoup: `soup.find('div', class_='rich_media_content').get_text()`
- Fallback: extract from JS variable `content_noencode` in the HTML
- Full workflow in `references/wechat-article-extraction.md`

**OCR extraction** (when boss sends portfolio screenshots):
```bash
apt-get install tesseract-ocr tesseract-ocr-chi-sim -y && pip install pytesseract
```
Resize image to width 600 before OCR. Use `lang='chi_sim+eng'`. Full flow in `references/stock-quotes-reference.md`.

### 5.3 Price Verification (Critical)

**⚠️ delegate_task sub-agents FABRICATE stock prices.** Always verify:
```python
browser_navigate(url='https://www.google.com/finance/quote/9988:HKG')
# Look for StaticText "$XXX.XX" in snapshot, followed by change %
```

### 5.4 Report Templates

Two report templates — one for each daily slot:

#### 午间快报模板 (12:00, ~800-1000 chars)

```markdown
# 🌅 九九财富午间速递 | YYYY-MM-DD | 周X | 午间版
*📌 [当日主题] · [市场关键信号]*
*数据截至上午收盘（A股11:30 / 港股12:00）*

---

## 📊 持仓追踪

Merged 3-market table: 标的 | 现价 | 半日涨跌 | 一句话判断
Focus on A-share and HK stocks (most data available); note US stocks from prior close.
0-1 key signal below table.

## ⚡ 各科技板块走势一览

Sector overview table: AI芯片 | AI应用 | 新能源 | 机器人/智驾 | AI基建链
Each row: 走势 indicator (🟢/🔴) + 亮点 (1 key stock move or news)
This replaces 上午盘异动速览 — boss prefers broad sector framing over isolated moves.

## 🧠 今日主题速递：[当日主题精简版]

~100-200 words, highest-signal insight from the day's theme.
Light version — don't need full comparison framework.

## 💰 午间操作建议

Action matrix: 操作 (🟢持仓不动/🟡逢低加仓/🔴观察减仓) | 标的 | 逻辑
Must include clear buy/hold/sell/reduce signals — this is the boss's highest-value section in the noon report.
Replace the generic 后市关注 with this.
```

#### 晚间复盘模板 (20:00, ~1200-1500 chars)

Full version — all markets closed, complete daily data.

**⚠️ CRITICAL: Section headings MUST use `## ` markdown format.** The `build.py` script's `extract_metadata()` function scans for `^## ([^\n]+)` regex to detect sections. Using `**bold**` headings instead of `## ` will silently break the build.py section index — no error message, just empty section metadata in the generated HTML. Always write section headings as `## 📊 持仓追踪` not `**📊 持仓追踪**`.

Target: **1200-1500 characters** in Chinese for regular weekdays, **1600-2000 characters** for weekend weekly recap. 5 required sections in order:

```markdown
# 🌅 九九财富晨报 | YYYY-MM-DD | 周X
*subtitle line — e.g., AI基建链深度复盘 — NVDA财报后市场反响*
*On Friday runs: subtitle should reference Thu close data — e.g. "基于5月21日收盘的一周复盘"*

---

## 📊 持仓追踪

Merged 3-market table: 标的 | 现价 | 涨跌幅 | 成本→浮亏率 | 一句话判断
0-2 key signals below table (bold with `>` blockquote prefix)

## 🧠 行业深度洞察：[当日主题]

200-400 words, must have comparison + attribution + actionable judgment.
Use comparison tables (e.g., 环节 vs 代表标的 vs 增速 vs PE vs 判断) for depth.

## 雷达池速览

US + HK + A-share radar, 1 line each in a table: 标的 | 价格 | 涨跌幅 | 信号

## ⭐ 本周精选潜力标的（2-3只深度分析）

Each: full 7-role framework (basic/technical/sentiment/bull/bear/trader/risk).
Use the 7-row table format per stock (维度 | 分析), NOT bullet lists.

## 💡 九九组合策略

Portfolio summary in RMB (USD:CNY=7, HKD:CNY=0.92).
Strategy A (aggressive) + Strategy B (conservative) with specific ticker actions.
**催化剂日历** table at bottom: 日期 | 事件 | 影响标的 | 重要性
```

Full template with strategy A/B format and 7-role framework in `references/market-watchlist-full.md`.

#### 🎯 Handling Boss Special Requests (老板特别交代)

When the boss adds explicit "重点看" or "特别看" items to the report prompt (e.g., "重点看小米持续走弱"):

1. **Weave into the standard template, don't replace it.** The special request is additional, not a replacement for the standard sections.
2. **Best integration point:** Add a专项分析 sub-section under the 🧠 行业深度洞察 section. Format as a H3 heading with the stock name (e.g., `### 🎯 小米（1810.HK）专项分析`).
3. **Structure for the专项分析:**
   - Opening: Today's price and change context (from verified data)
   - Core pressure factors (🔴 bullets)
   - Positive catalysts (✅ bullets)
   - Support/resistance levels (支撑位/压力位)
4. **Do NOT skip the scheduled deep-dive theme** — the boss's special request is an addition, not a replacement. If the special stock happens to be in the day's theme, it naturally overlaps.
5. **Keep it concise** — 100-200 words max for the special analysis, nestled within the 200-400 word deep-dive section.
6. **2026-05-28 session example:** Boss requested Xiaomi analysis on a Thursday (AI基建链 day). The report kept the AI infra chain as the main deep-dive theme, added a `### 🎯 小米（1810.HK）专项分析` section underneath, and included Xiaomi data in the holdings table and strategy sections per usual.

#### Weekend variant template (周末复盘):

#### Saturday Weekly Recap template:
```markdown
# 🌅 九九财富晨报 | YYYY-MM-DD | 周六
*📌 周末特辑 · 本周全市场深度复盘 & 下周展望*
*基于5月XX日（周五）收盘数据*

---

## 📊 持仓追踪 · 周度总览

Merged 3-market table with all holdings (price | change | cost→unrealized% | 1-sentence call)
Combo summary line below table (总资产, 总浮动盈亏, which market is holding up/dragging down)

## 🧠 行业深度洞察：周度复盘 — [本周主题]

Week-in-review: cover Mon-Fri key events for the day's theme. Must include comparison + attribution + actionable judgment. 200-400 words.

## 雷达池速览：

US + HK + A-share radar, 1 line each

## ⭐ 下周潜力标的（2只深度分析）

Each: full 7-role framework. Prioritize stocks with catalysts in the coming week (e.g., earnings this week).

## 💡 九九组合策略

Portfolio summary in RMB, action matrix (持有/观察/减仓/关注)

## 📌 下周催化剂

Date table: event | impacted stocks | importance
```

#### Sunday Preview template (use when Saturday already ran):
```markdown
# 🌅 九九财富晨报 | YYYY-MM-DD | 周日
*📌 明日开市 · 全周前瞻 — [2-3 key themes]*
*基于5月XX日（周五）收盘数据，本周焦点：[top 2 catalysts]*

---

## 📊 持仓追踪 · 前瞻速览

Same merged 3-market table but frame as forward look. Add ⭐ catalyst emphasis in the "一句话判断" column for stocks with near-term events (e.g., "5/26 Q1财报 — 全周最大催化剂").

## 🧠 行业深度洞察：周度前瞻 — 未来一周的[Number]条主线

Numbered forward-looking themes (4-6). Each: catalyst event → affected positions → scenario analysis. NOT a week-in-review.

## 雷达池速览

Same format.

## ⭐ 本周潜力标的（2只深度分析）

Same 7-role framework, prioritize COMING WEEK catalysts.

## 💡 九九组合策略

Same strategy A/B format. Action matrix (持有/观察/减仓/关注).

## 📌 本周催化剂

Date table: Mon-Fri events for the coming week.
```


### 5.4a Cron Job Delivery Failure Recovery

The two cron jobs (午间快报 `cfcb3b83b5d2` at `0 12 * * *`; 晚间复盘 `96132ae625ba` at `0 20 * * *`) may run successfully but fail on delivery (e.g., WeChat rate limit). The actual report content IS generated — it just doesn't reach the user.

**Recovery workflow when last_status = "error" due to delivery failure:**

1. **Check cron status first:**
   ```
   cronjob(action="list")
   ```
   Look for `last_status: "error"` and `last_delivery_error` containing "rate limited" or similar delivery-level errors (not generation-level errors like 402/401).

2. **Do NOT try to recover the lost cron output** — the report was generated inside the cron prompt and isn't stored as a file (unless `~/.hermes/cron/output/` has it). Instead, **regenerate from scratch** using the current day's theme and the latest market data.

3. **Data collection is identical to a fresh run:**
   - A-share: `qt.gtimg.cn` (Tencent API) — fastest, no rate limit
   - HK/US stocks: `browser_navigate` → Google Finance
   - Industry deep-dive: `delegate_task` for research (or compose from knowledge)
   - Use today (Beijing time) as the report date

4. **Watch out for ticker ambiguity when regenerating:**
   - AI智能ETF = `sh515070` (confirmed via session_search)
   - If unsure about a ticker, use Tencent API to probe candidate codes + session_search to confirm from past morning reports

5. **Delivery after regeneration:**
   - Write report to `reports/YYYY-MM-DD.md` in the repo
   - Run `build.py` → git add/commit/push
   - Deliver directly in the current Feishu conversation (you're talking to the user right now)

### 5.5 GitHub Pages Deployment

When publishing to GitHub (repo `corinwe/wealth-invest-daily`, Pages at `corinwe.github.io/wealth-invest-daily`):

**File naming convention:**
- 午间快报 (12:00): `reports/YYYY-MM-DD-noon.md`
- 晚间复盘 (20:00): `reports/YYYY-MM-DD.md`

Both files are committed alongside `index.html` and `report.html` generated by `build.py`.

**Repo location:** The actual repo lives at `~/wealth-invest-daily` (not `/tmp/wealth-invest-daily`).

```bash
# 1. Write report (using write_file tool)
write_file ~/wealth-invest-daily/reports/YYYY-MM-DD.md <content>

# 2. Handle any unstaged changes before rebase (common when file was just written)
cd ~/wealth-invest-daily && git add -A && git stash && git pull --rebase origin main && git stash pop

# 3. Build HTML
cd ~/wealth-invest-daily && python3 build.py

# 4. Git commit + push
cd ~/wealth-invest-daily && \
git add -A && \
git diff --cached --quiet || (
  git commit -m "📈 九九财富投资晨报 - $(date +%Y-%m-%d)" && \
  git push origin main
)
```

**Pitfalls:**
- `.nojekyll` file **must** exist in repo root — without it GitHub Pages rejects subdirectory `.md` files (see `references/github-pages-nojekyll.md`)
- SSH key must be added to GitHub (see `references/ssh-github-setup.md`)
- Cron `script:` parameter persists on update — pass `script=""` (empty string) to clear
- `build.py` requires `pip install edge-tts`
- Use `git add -A` (not single-file), because `index.html` and `report.html` also need committing
- **git pull --rebase with unstaged changes:** If `write_file` has already modified the report file before running the deployment commands, `git pull --rebase origin main` will fail with "cannot pull with rebase: You have unstaged changes". Fix: `git add -A && git stash && git pull --rebase origin main && git stash pop` before running build.py.
- **Sibling subagent file conflict:** When writing a report file, a warning like "was modified by sibling subagent" may appear. This happens when multiple subagents (from delegate_task or previous cron runs) write to the same file path concurrently. Write the daily report file from the main thread after all delegate_task calls complete, not inside a delegate_task sub-agent.

### 5.6 SSH Key & Provider Fallback Setup

- `references/ssh-github-setup.md` — SSH key regeneration, GitHub setup, key mismatch diagnosis
- `references/provider-fallback-config.md` — OpenRouter as fallback provider config
- `references/github-push-setup.md` — Full GitHub delivery setup guide (gh CLI + token auth variant)

## 6. Portfolio Analysis Workflow

### 6.1 Data Collection Strategy

When user provides holdings and wants a comprehensive analysis:

**Step 1: Try `yfinance` first** (most reliable)
```python
import yfinance as yf
sp = yf.Ticker('^GSPC')
# info dict: regularMarketPrice, regularMarketChangePercent, regularMarketPreviousClose
```

**Step 2: Fallback to `browser_navigate` → Google Finance**
URL format by market:
- US stocks: `https://www.google.com/finance/quote/{TICKER}:NASDAQ` (or :NYSE)
- Indices: `https://www.google.com/finance/quote/.INX:INDEXSP` (S&P 500)
- HK stocks: `https://www.google.com/finance/quote/{CODE}:HKG`
- A-Shares (深交所): NOT supported by Google Finance — use alternative sources
- A-Shares (上交所): Also NOT supported

**Known pitfalls:**
- Yahoo Finance rate-limits aggressively — use `browser_navigate` as fallback
- `yfinance` needs crumb authentication, fails if called too fast
- Google Finance doesn't support Shenzhen/Shanghai A-shares (000333.SZ, 002594.SZ)
- Google Finance HK stocks use HKG suffix, not HKEX
- **Google Finance index URL patterns vary:** HSI uses `HSI:INDEXHANGSENG` (not `.HSI:INDEXHANGSENG` — dot prefix returns 404). S&P 500 uses `.INX:INDEXSP`. NASDAQ uses `.IXIC:INDEXNASDAQ` (NOT `^IXIC:INDEXNASDAQ` — the caret-prefixed variant returns 404 "Page Not Found"). Test the URL; if it returns a 404/not-found page, use the Google Finance search box to find the correct ticker format.
- **Google Finance also doesn't support futures/commodity indices** — use web_search instead
- **Bing search can be used as alternative when Google is blocked** via `browser_navigate(url='https://www.bing.com/search?q=...')`
- **Browser-based search is fragile** — Google/Bing may present CAPTCHA or redirect to "sorry" pages or Cloudflare challenges. When this happens:
  - For Chinese ticker/name lookups: use Tencent API to probe candidate codes (`curl -s "https://qt.gtimg.cn/q=szCODE,shCODE"`) + `session_search` to confirm identities from past reports
  - For broader searches: try `bing.com/news/search?q=...` (news tab bypasses some CAPTCHAs), or use a different query formulation
  - As last resort: search `eastmoney.com` or other Chinese financial sites

**Step 3: For A-share data**
- Best alternative: Chinese financial data APIs (akshare, tushare)
- Or: manual web search with `web_search` or `browser_navigate` to eastmoney.com
- Or: Google Finance for the **H-share** listing of the same company (e.g., BYD 1211.HKG 🇭🇰) as a price reference, noting H-shares trade at a discount to A-shares

### 6.2 Analysis Report Template

When presenting portfolio analysis, use this structured format:

```markdown
# 🏦 持仓全景分析报告
**📅 数据时间：** YYYY年M月D日

## 一、🌍 市场大盘概况
| 指数 | 最新点位 | 涨跌 |
|-----|---------|------|
| 标普500 | X | +/-Y% |
| 纳指/道指 | X | +/-Y% |
| 港股/其他 | X | +/-Y% |

## 二、📋 持仓盈亏一览
| 股票 | 买入价 | 现价 | 盈亏 | 幅度 |
|-----|:-----:|:----:|:----:|:----:|
| TICKER | $X | $Y | -$Z | -W% 🔴/🟢 |

## 三、🔍 个股深度分析
每只股票用两栏格式：
**好的一面：** ✅ bullet points
**坏的一面：** ⚠️ bullet points
**九九评价：** ⭐X/5 + concise recommendation

## 四、🎯 综合评估与建议

### 投资风格诊断
One paragraph assessment of user's style (growth/value, concentrated/diversified, entry timing)

### 组合打分
| 维度 | 评分 | 说明 |
|:---|:---:|:-----|
| 赛道选择 | ⭐⭐⭐⭐⭐ | 方向判断 |
| 分散程度 | ⭐⭐⭐ | 跨市场/跨行业 |
| 买入时机 | ⭐⭐ | 入场点位 |
| 风险控制 | ⭐⭐ | 单一风险敞口 |
| 长线潜力 | ⭐⭐⭐⭐ | 基本面判断 |

### Action Matrix
| 动作 | 标的 | 理由 |
|:---|:----|:-----|
| 🟢 坚定持有 | TICKER | 理由 |
| 🟡 观察持有 | TICKER | 催化剂待验证 |
| 🔴 考虑减仓 | TICKER | 基本面恶化 |
| 🆕 可考虑增配 | TICKER | 补上产业链缺口 |
```

### 6.3 Key Reading Patterns to Flag

When analyzing a portfolio, watch for these archetypes:

| Pattern | Signal | Typical Advice |
|---------|--------|----------------|
| **Good picks, bad entry** | Right stock, wrong price (MSFT at $500+) | Hold + DCA down, don't panic sell |
| **Fundamental break** | Accounting scandal, guidance withdrawal (ICLR) | Consider stop-loss, this isn't a normal dip |
| **Cycle-driven** | Industry downcycle, competitive pressure (美团) | Reduce if no catalyst in sight |
| **Multi-bagger** | Bought low, huge gains (BYD A-share) | Take partial profits or set trailing stop |
| **Sector bet via ETF** | Broad index + thematic ETF | Check ETF holdings — may overlap with single-stock positions |

## Pitfalls
1. **Memory is tiny (2,200 chars)** — must aggressively prune old project logs before adding new role config. Old detailed todo-lists and progress logs belong in session history, not persistent memory.
2. **Feishu delivery may fail silently** — verify cron job creation response includes `"state": "scheduled"` and a `next_run_at` timestamp.
3. **Chinese-language persona prompts** — the cron prompt must be in the user's language (usually Chinese) for natural-sounding reports. Don't default to English.
4. **Dual-schedule filename ambiguity** — The noon report writes to `YYYY-MM-DD-noon.md` while the evening report writes to `YYYY-MM-DD.md`. When recovering from a delivery failure, confirm which SLOT failed first — don't overwrite the evening file with a noon recovery or vice versa.
5. **Noon report data limitation** — At 12:00 Beijing time, A-shares have only morning session data (9:30-11:30) and HK has morning session (9:30-12:00). US data is from prior close. DO NOT present the noon report as a full-day update. The subtitle must clearly state data cuts (e.g., "数据截至当天上午收盘").
4. **No portfolio data yet** — this skill covers *setting up* the assistant. Actual portfolio management workflows (position tracking, rebalancing, risk analysis) require separate skill extensions.
5. **One `remove` at a time** — the memory tool doesn't support bulk delete. For a clean slate in a full memory, expect 20-30+ individual remove calls.
6. **Data collection rate limits** — Yahoo Finance API rate-limits aggressively. Browser scrape via `browser_navigate` to Google Finance is the reliable fallback for US/HK stocks. A-shares need Chinese data sources (eastmoney, akshare).
7. **Google Finance doesn't support A-shares** — Shenzhen stock codes (000XXX, 002XXX) and Shanghai (600XXX) cannot be queried. Use web_search or Chinese financial sites instead.
8. **Portfolio analysis is a large turn cost** — querying 7+ stocks individually via browser_navigate consumes significant tokens. Batch efficiently, use `delegate_task` for parallel lookups if feasible.
9. **Ticker name ambiguity risk** — Chinese nicknames for stocks can be ambiguous (e.g., "益康" could mean ECL Ecolab or ICLR ICON). Always confirm the ticker symbol with user before doing deep analysis. If wrong, update memory and redo immediately.
10. **CRITICAL: Two layers of delegate_task fabrication: (a) PRICES and (b) EARNINGS/NARRATIVE** — Sub-agents fabricate at two levels with different detection patterns:
    - **(a) Price fabrication:** When sub-agents *don't* use browser_navigate, they hallucinate prices — sometimes severely. 2026-05-25 session data:
      - **Meituan 3690: sub-agent claimed HKD 168.30 vs actual HKD 81.35 — 107% error (more than 2x!)**
      - **Alibaba 9988: sub-agent claimed HKD 118.50 vs actual HKD 127.00 — 7% error**
      - **Xiaomi 1810: sub-agent claimed HKD 32.85 vs actual HKD 30.00 — 9% error**
      - Earlier: Xiaomi ~48→actual 31.46, Alibaba ~138→actual 133.30, NVDA ~$97→actual $220 (stock split confusion)
      - **Do not assume prices are "close" (within 5%)** — errors can exceed 100%. The only way to verify is scraping Google Finance directly via `browser_navigate`.
    - **(b) Earnings/narrative fabrication:** Even when sub-agents DO use browser_navigate and get prices correct (e.g., NVDA $215.33 ✓), they fabricate detailed earnings numbers and narrative context. In the 2026-05-23 run, the sub-agent claimed NVDA FY2026Q1 revenue of $43.2B but the actual Google Finance-verified data was $81.6B (a 90% error). In the 2026-05-25 run, the AI chip industry deep-dive sub-agent claimed NVDA revenue of ~$42B and EPS $2.82, while actual Google Finance data showed $81.6B revenue and EPS $1.87 — both numbers wrong. The earnings summary text is AI-generated fiction, not scraped data.
    - **Rule:** browser_navigate gives you real prices and summary blurbs. Everything else from delegate_task about earnings numbers, revenue breakdowns, financial details, and market commentary is hallucinated. Verify all earnings data by reading the Google Finance page directly.
11. **NVDA stock split confusion** — NVDA did a 10:1 split June 2024. Sub-agents may return pre-/post-split prices inconsistently (~$97 = pre-split price that no longer exists). Always scrape live price from Google Finance.
12. **Cron job re-run: file already exists** — The repo may contain a report for today's date from a prior run. Overwrite it with fresh data from the latest close. Use `write_file` same path, then git add/commit/push normally.
13. **REPORT HEADINGS MUST USE `## ` NOT `**bold**`** — The `build.py`'s `extract_metadata()` scans for `^## ([^\n]+)` regex. If you write `**📊 持仓追踪**` instead of `## 📊 持仓追踪`, the HTML index will have empty section metadata. No error is raised — it fails silently. This is the #1 formatting mistake.
14. **git pull --rebase before commit** — Always `git pull --rebase origin main` before build+push. The cron job may not have run for several days and the remote may have moved ahead. Push will fail with non-fast-forward error if you skip this step.
15. **300ETF ticker ambiguity** — The portfolio has **510300** (Shanghai 沪深300ETF) with cost ¥4.571. But some reports have used **159300** (Shenzhen-listed 沪深300ETF). These are different ETFs tracking the same index. Verify which one is owned: `session_search` for past reports to find the correct ticker, or use Tencent API to check both `sh510300` and `sz159300`.
16. **NVDA after-hours price — the 20:00 evening slot captures this naturally** — When NVDA reports earnings (often Tuesday/Wednesday after US close at 16:00 ET = 04:00 Beijing +1), the 20:00 Beijing evening report is published AFTER the US regular session opened again (US opens 21:30 Beijing, so at 20:00 Beijing the US hasn't opened yet). The latest NVDA data at 20:00 Beijing is the pre-market price from the same day. This is a meaningful improvement over the old 8:00 AM slot which could only report stale after-hours data. For the noon (12:00) slot, NVDA after-hours from the previous night is the freshest data available.
17. **🚨 Cron date mismatch: ALWAYS run `date` first.** The cron prompt template hardcodes a date (e.g., "今天是2026年5月27日周三") but the system clock may differ. In the 2026-05-28 session, the prompt said Wednesday May 27 but the system was Thursday May 28. This changes the deep-dive theme (use Thursday's AI基建链, not Wednesday's 新能源+机器人) and data freshness expectations. Run `date` as the first step of any cron execution.
- **GPU cost** — heavy browser_navigate usage ($5.7/1M tokens for browser agent) can add up. Be strategic: verify 3-4 key prices per run rather than all 10+ holdings. However, do NOT assume sub-agent prices are "close" — the 2026-05-25 session showed a 107% error on Meituan (HKD 81.35 actual vs HKD 168.30 hallucinated). Prioritize verification of: (1) large-move or earnings stocks (NVDA after-hours), (2) stocks where sub-agent prices seem unusual (too high/low vs prior day), (3) stocks where NVDA split confusion is possible.
- **delegate_task research loses full content** — when using `delegate_task` for the industry deep-dive (Task D), the sub-agent's research output is **summarized**, not returned verbatim. The summary may say "delivered inline" but the actual analysis text is gone. Fix: either (a) ask the sub-agent to write findings to a temp file and then read it, or (b) do the research yourself with `web_search` instead of delegating. The deep-dive section is the report's highest-value section — don't trust it to a summary surrogate.
- **Weekend cron runs — Saturday vs Sunday distinction critical** — The cron schedule fires at 12:00 and 20:00 on Saturday AND Sunday when markets are closed. Both time slots use the same Friday-close data on weekends. The evening (20:00) report is the PRIMARY weekend report since noon and evening would have near-identical data. On Saturday (first post-market day): produce the full weekly recap covering Mon-Fri events. On Sunday (second post-market day): produce a Sunday Preview focused on the coming week's catalysts, NOT another recap. See §5.4 Weekend variant for both templates.
- **delegate_task max_concurrent_children** — default is 3, skill expects 4. Either increase it in config or split into two batches.
- **Google Finance HSI URL** — the correct format for Hang Seng Index is `HSI:INDEXHANGSENG` (without dot prefix). The dot-prefixed variant `.HSI:INDEXHANGSENG` returns 404 "Page Not Found". Verified working: `https://www.google.com/finance/quote/HSI:INDEXHANGSENG`.
- **US holiday mixed data freshness (Memorial Day, July 4th, Labor Day, Thanksgiving)** — When the US market is closed for a holiday but A-shares trade normally, both daily reports must handle 3-way data staleness (US stale, A-shares fresh). The noon report benefits most here: A-share morning session data IS fresh. The subtitle MUST explain discrepancies explicitly (e.g., "基于5月22日（美/港）及5月25日收盘（A股）数据").
