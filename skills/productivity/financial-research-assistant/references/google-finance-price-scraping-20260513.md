# Google Finance Price Scraping Reference — 2026-05-13

## Purpose

This file records concrete price data verified via Google Finance `browser_navigate` scraping during the 2026-05-13 morning briefing. It serves as a calibration dataset — future sessions can cross-reference their scraped prices against these to detect data source issues.

## Verifiable Prices (May 12 Close — Google Finance)

### US Stocks
| Ticker | Google Finance Price | Sub-agent Hallucinated | Delta | Notes |
|--------|--------------------|----------------------|-------|-------|
| NVDA | $220.78 (close +0.61%) | ~$97 (sub-agent) | $123.78 diff | Sub-agent confused by 10:1 stock split (June 2024). Pre-split equivalent of $220.78 = ~$22.08 |
| MSFT | $382.24 (-0.35%) | ~$425-430 (old report) | ~$43 diff | Old report was weeks stale |
| ECL | $244.68 (+0.42%) | ~$240-245 (old report) | ~$5 diff | Reasonable, old report was close |

### HK Stocks
| Ticker | Google Finance Price | Sub-agent Hallucinated | Delta | Notes |
|--------|--------------------|----------------------|-------|-------|
| Alibaba 9988.HK | $133.30 HKD (0.00%) | ~138.50 (sub-agent) | ~$5 diff | Sub-agent was in ballpark but off |
| Xiaomi 1810.HK | $31.46 HKD (0.00%) | ~48.20 (sub-agent) | $16.74 diff | Sub-agent massively overestimated. May have confused USD with HKD or used stale data |
| Meituan 3690.HK | $84.15 HKD (0.00%) | ~155-160 (old report) | ~$73 diff | Old report was completely fabricated — 美团 never traded near 155-160 recently (52wk high $149.80, 52wk low $73.60) |

## Key Observations

1. **Google Finance "0.00%" is for the current day if market hasn't opened** — HK stocks show 0.00% because the session was captured before HK market opening on May 13. The displayed price IS the May 12 close.

2. **US after-hours prices differ from close** — NVDA after-hours shows $219.48 (-0.59%) vs close of $220.78 (+0.61%). Always report the **Close** price for daily briefings, not after-hours.

3. **Google Finance URL patterns that work:**
   - US: `https://www.google.com/finance/quote/NVDA:NASDAQ`
   - HK: `https://www.google.com/finance/quote/9988:HKG`
   - Indices: `https://www.google.com/finance/quote/.INX:INDEXSP` (but this can fail; use web_search as fallback)

4. **Google Finance URL patterns that do NOT work:**
   - A-shares: `https://www.google.com/finance/quote/002594:SZX` → "Page Not Found"
   - HK index: `https://www.google.com/finance/quote/.HSI:INDEXHK` → "Page Not Found"

5. **Rate-limiting note** — calling Google Finance for 5+ tickers in rapid succession via `browser_navigate` did NOT trigger rate limiting in this session. Yahoo Finance blocked immediately (Too Many Requests on the first call).

6. **Extracting prices from Google Finance page** — The price appears as a StaticText element right after the company name. Look for the text pattern: `"Stock Name"`, then `"$XXX.XX"`, then `"+X.XX%"` or `"0.00%"`. The exact page structure varies between US/HK tickers and their first-load vs reload state.

## NVDIA Stock Split Details

Important for future price verification:

- NVDA 10:1 stock split executed June 7, 2024 (after close)
- Pre-split price (~$97 reported by sub-agent) corresponds to ~$970 pre-split, which is a reasonable price for NVDA in early 2024
- Current post-split price ($220.78) means the stock has roughly doubled since the split
- If a sub-agent returns ~$97 for NVDA, they are likely returning pre-split pricedata or confused by a different date
- **Rule: always scrape NVDA's current price. Never trust a sub-agent's NVDA number.**

## Actionable Rules for Future Morning Briefings

1. Always scrape ALL holding prices from Google Finance after delegate_task returns — use browser_navigate for each ticker
2. Cross-check sub-agent prices against scraped prices. If delta > 5%, scrap the sub-agent price and use the scraped one
3. For A-shares (not available on Google Finance), use the H-share listing as a rough proxy (e.g. BYD 1211.HK), noting that H-shares trade at a discount
4. Report the Close price (not after-hours) for US stocks
5. If the market is open, the price shown may be intraday; note "intraday" in the report
