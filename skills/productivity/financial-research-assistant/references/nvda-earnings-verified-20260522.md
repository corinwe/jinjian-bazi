# NVDA Earnings Verified via Google Finance Scrape (2026-05-22)

**Source:** Google Finance scrape for `NVDA:NASDAQ` on 2026-05-22 (Friday close)
**Earnings report date:** 2026-05-20 (Wednesday after close)
**Earnings period:** Q1 FY2027 (Feb-Apr 2026 quarter)

## Verified Data

| Metric | Value |
|--------|-------|
| **Revenue** | $81.6B (+85% YoY) |
| **EPS beat** | +5.54% |
| **Revenue beat** | +3.16% |
| **Q2 Guidance** | ~$91B |
| **Stock (5/22 close)** | $215.33 (-1.90% on day, -$4.18) |
| **After-hours (5/22)** | $214.28 (-0.49%) |

## Google Finance Blurb Summary

> "NVIDIA rose approximately 10% this past month, fueled by a record-breaking May 2026 earnings report and increased demand for Blackwell chips. Analysts project continued upward momentum in the next quarter as market sentiment suggests hyperscaler capital expenditure and the upcoming Vera Rubin platform will sustain triple-digit data center growth."

### Bullish Highlights (from Google Finance)
- **Revenue:** Record Q1 revenue of $81.6B, 85% YoY, beat estimates
- **Q2 guidance:** ~$91B, signaling sustained demand
- **Capital return:** 25x dividend hike, $80B added to buyback authorization
- **Product:** Blackwell transition accelerating, pipeline >$1T, Vera Rubin platform

### Bearish Highlights (from Google Finance)
- **Supply chain:** HBM and advanced packaging bottlenecks
- **Geopolitical:** Export controls continued
- **Valuation:** High expectations already priced in

## Calibration Against Sub-Agent Fabrication

On 2026-05-23 session, the delegate_task sub-agent for "industry deep-dive" reported:

| Metric | Sub-Agent Claim (HALLUCINATED) | Actual (Verified) | Error |
|--------|------|--------|-------|
| Revenue | $43.2B | $81.6B | **-47%** |
| Revenue YoY | +68% | +85% | **-17pp** |
| Data Center revenue | $38.5B | Not on page | N/A |
| Net Income | $19.8B | Not on page | N/A |
| Stock price (5/22) | $215.33 | $215.33 | **0%** ✅ |

**Pattern:** Sub-agents got the stock price exactly right (used browser_navigate) but fabricated all earnings details. The fabricated revenue was roughly half the actual figure.

## Actionable Rules

1. **Never trust delegate_task earnings numbers** — they fabricate detailed financial metrics even when prices are correct.
2. **Scrape NVDA earnings data directly from Google Finance** — the page shows earnings badge (EPS/revenue beat %) and analysis blurbs.
3. **Use the price + the Google Finance earnings summary blurb** (extracted from browser snapshot static text) — these are the only reliable data points.
4. **Ignore any $/percentage breakdowns from sub-agents** — they make up plausible-looking numbers that are wrong by 50%+.
