# Google Finance Price Scraping Reference — 2026-05-16

## Purpose

Verified price data from Google Finance `browser_navigate` scraping during the 2026-05-16 morning briefing (Saturday cron run). Provides calibration data for Friday May 15 close — the most recent available data.

## Verifiable Prices (May 15 Close — Google Finance)

### US Stocks

| Ticker | Close Price | Change | Prev Close | Google Finance URL |
|--------|------------|--------|------------|-------------------|
| **NVDA** | $225.32 | -4.42% (-$10.42) | $235.74 | `quote/NVDA:NASDAQ` ✅ |
| **MSFT** | $421.92 | +3.05% (+$12.49) | $409.43 | `quote/MSFT:NASDAQ` ✅ |
| **ECL** | $247.62 | -0.53% (-$1.32) | $248.94 | `quote/ECL:NYSE` ✅ |
| **AVGO** | $425.19 | -3.32% | $439.79 | `quote/AVGO:NASDAQ` ✅ |
| **AMD** | $424.10 | -5.69% | $449.70 | `quote/AMD:NASDAQ` ✅ |
| **GOOGL** | $396.78 | -1.07% | $401.07 | `quote/GOOGL:NASDAQ` ✅ |

### Indices

| Index | Close | Change % | URL |
|-------|-------|---------|-----|
| **S&P 500** | 7,408.50 | -1.24% | `quote/.INX:INDEXSP` ✅ |
| **NASDAQ Composite** | 26,225.15 | -1.54% | `quote/^IXIC:INDEXNASDAQ` ✅ |

### HK Stocks

| Ticker | Close Price (HKD) | Change | Prev Close | Google Finance URL |
|--------|------------------|--------|------------|-------------------|
| **Alibaba 9988** | $132.30 | -4.06% (-$5.60) | $137.90 | `quote/9988:HKG` ✅ |
| **Xiaomi 1810** | $30.70 | -3.22% (-$1.02) | $31.72 | `quote/1810:HKG` ✅ |
| **Meituan 3690** | $82.70 | -3.50% (-$3.00) | $85.70 | `quote/3690:HKG` ✅ |
| **NIO 9866** | $49.28 | -1.36% (-$0.68) | $49.96 | `quote/9866:HKG` ✅ |
| **Tencent 0700** | $456.40 | +0.33% (+$1.50) | $454.90 | `quote/0700:HKG` ✅ |

### A-Shares (via Tencent API)

| Ticker | Close Price (CNY) | Change % | Prev Close |
|--------|------------------|---------|------------|
| **比亚迪 002594** | ¥96.30 | -2.46% | ¥98.73 |
| **美的集团 000333** | ¥82.57 | +0.93% | ¥81.81 |
| **中际旭创 300308** | ¥1,049.87 | -2.61% | ¥1,078.00 |
| **宁德时代 300750** | ¥423.60 | -0.80% | ¥427.00 |
| **赛力斯 601127** | ¥83.26 | -2.10% | ¥85.05 |
| **300ETF 510300** | ¥4.878 | -1.28% | ¥4.941 |
| **AI智能ETF 515070** | ¥2.466 | -2.22% | ¥2.522 |
| **上证指数 000001** | 4,135.39 | -1.02% | 4,177.92 |
| **深证成指 399001** | 15,561.37 | -1.17% | 15,745.74 |

## Key Learnings This Session

1. **Sub-agent price accuracy was GOOD this time** — All sub-agent prices were within 1-2% of verified values. This is a significant improvement over the 2026-05-13 session where major hallucinations occurred (NVDA ~$97 vs actual ~$221). The sub-agent may have been more careful or the prompt instruction was clearer.

2. **Still always verify** — Even with improved accuracy, independent verification caught the exact change percentages and confirmed no split confusion. The cost of verification (3-4 browser_navigate calls) is small relative to the risk of publishing wrong prices.

3. **Google Finance URL patterns confirmed:**
   - `quote/NVDA:NASDAQ` — works, shows close price with timestamp
   - `quote/9988:HKG` — works, shows HKD price with UTC+8 timestamp
   - `quote/ECL:NYSE` — works for NYSE-listed stocks
   - `.INX:INDEXSP` — works for S&P 500
   - `^IXIC:INDEXNASDAQ` — works for NASDAQ Composite
   - **HSI NOT verified this session** — sub-agent used `.HSI:INDEXHANGSENG` via search box

4. **After-hours data:** NVDA after-hours = $224.41 (-0.40%), MSFT after-hours = $419.67 (-0.53%). Report the Close price for daily reports, not after-hours.

5. **Tencent API timing:** The `qt.gtimg.cn` data timestamp shows `202605151614XX` = May 15, 16:14 — consistent with the market close. The API is reliable for same-day close data.
