# Google Finance Price Scraping — 2026-05-25 Session (May 22 Close)

**Session date:** 2026-05-25 (Monday 8:00 AM Beijing time)
**Data date:** 2026-05-22 (Friday close — last trading session before report)

## Why This Matters

This session produced the most severe sub-agent price fabrication seen to date: **Meituan 3690 was hallucinated at HKD 168.30 when the actual price was HKD 81.35 — a 107% error.** This disproves the earlier assumption that sub-agent prices are "usually close-ish (within 5%)."

## Verified Google Finance Prices

### HK Stocks (via `browser_navigate` → `quote/{CODE}:HKG`)

| Stock | Ticker | Actual Price | Change | Timestamp |
|:------|:------:|:------------:|:------:|:---------:|
| Alibaba | 9988:HKG | **HKD $127.00** | +0.79% | May 22, 4:08 PM UTC+8 |
| Xiaomi | 1810:HKG | **HKD $30.00** | +1.15% | May 22, 4:08 PM UTC+8 |
| Meituan | 3690:HKG | **HKD $81.35** | -0.91% | May 22, 4:08 PM UTC+8 |
| NIO | 9866:HKG | **HKD $42.78** | -0.42% | May 22, 4:08 PM UTC+8 |
| Tencent | 0700:HKG | **HKD $441.40** | +0.55% | May 22, 4:08 PM UTC+8 |

### US Stocks (via `browser_navigate` → `quote/{TICKER}:{EXCHANGE}`)

| Stock | Ticker | Actual Price | Change | After-hours | Timestamp |
|:------|:------:|:------------:|:------:|:-----------:|:---------:|
| Microsoft | MSFT:NASDAQ | **$418.57** | -0.12% | $417.80 (-0.18%) | May 22, 4:00 PM ET |
| Ecolab | ECL:NYSE | **$253.32** | +1.26% | $255.00 (+0.66%) | May 22, 4:00 PM ET |
| NVIDIA | NVDA:NASDAQ | **$215.33** | -1.90% | $214.28 (-0.49%) | May 22, 4:00 PM ET |
| Broadcom | AVGO:NASDAQ | **$414.14** | -0.10% | $413.04 (-0.27%) | May 22, 4:00 PM ET |
| AMD | AMD:NASDAQ | **$467.51** | +3.99% | $462.81 (-1.01%) | May 22, 4:00 PM ET |
| Alphabet | GOOGL:NASDAQ | **$382.97** | -1.21% | $382.26 (-0.19%) | May 22, 4:00 PM ET |

### Indices (via `browser_navigate`)

| Index | Ticker | Actual Price | Change |
|:------|:------:|:------------:|:------:|
| Hang Seng | HSI:INDEXHANGSENG | **25,606.03** | +0.86% |
| S&P 500 | .INX:INDEXSP | **7,473.47** | +0.37% |
| Dow Jones | (shown on S&P page) | **50,579.70** | +0.58% |

### A-Shares (via Tencent API `qt.gtimg.cn` — reliable, verified)

| Stock | Code | Actual Price | Change |
|:------|:----:|:------------:|:------:|
| 比亚迪 | sz002594 | **¥93.75** | +0.26% |
| 美的 | sz000333 | **¥80.28** | -1.50% |
| 中际旭创 | sz300308 | **¥1,037.98** | +4.49% |
| 宁德时代 | sz300750 | **¥411.16** | -0.11% |
| 赛力斯 | sh601127 | **¥82.03** | -1.62% |
| 300ETF | sh510300 | **¥4.862** | +1.12% |
| AI智能ETF | sh515070 | **¥2.505** | +2.58% |
| 上证指数 | sh000001 | **4,112.90** | +0.87% |
| 深成指 | sz399001 | **15,597.30** | +2.30% |

## Sub-Agent Hallucination Comparison

| Stock | Sub-Agent Claimed | Google Finance Actual | Error |
|:------|:-----------------:|:---------------------:|:-----:|
| Meituan 3690 | HKD 168.30 | HKD 81.35 | **+107%** |
| Alibaba 9988 | HKD 118.50 | HKD 127.00 | -7% |
| Xiaomi 1810 | HKD 32.85 | HKD 30.00 | +9% |
| NVDA (earnings) | ~$42B rev, EPS $2.82 | $81.6B rev, EPS $1.87 | Rev -49%, EPS +51% |

**Key takeaway:** The sub-agent for HK stocks was dramatically wrong on Meituan (more than 2x the real price). The earnings hallucination was less severe than the 2026-05-23 session (49% vs 90% revenue error) but both revenue AND EPS were wrong. Always verify with `browser_navigate`.

## Google Finance NVDA Earnings Display Note

As of May 2026, the NVDA Google Finance page directly displays:
- `Q1 2027 earnings • EPS beat +5.54% • Revenue beat +3.16%`
- Summary blurb: "record Q1 revenue of approximately $81.6 billion, an 85% year-over-year increase"
- After-hours price displayed as separate line: `$214.28 -0.49% (-1.05) After hours · 7:59 PM`

This is the single most important Google Finance page for morning briefings because:
1. It shows the actual earnings numbers (not sub-agent hallucinations)
2. After-hours price captures market reaction to earnings (often more relevant than close)
3. Bullish/bearish sections provide structured narrative context
