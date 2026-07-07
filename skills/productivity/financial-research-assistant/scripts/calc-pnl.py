#!/usr/bin/env python3
"""
Portfolio P&L Calculator for 九九 Wealth Morning Briefing.

Usage: python3 scripts/calc-pnl.py [price_data.json]

If no argument, runs in interactive mode reading from stdin.
Expected input format (JSON):
{
  "hk": [{"name": "小米集团", "shares": 1600, "cost": 40.80, "price": 30.70}],
  "us": [{"name": "微软 MSFT", "ticker": "MSFT", "shares": 8, "cost": 501.09, "price": 421.92}],
  "cn": [{"name": "美的集团", "code": "000333", "shares": 1000, "cost": 69.886, "price": 82.57}]
}

Notes:
- Xiaomi: 2 accounts — account1 200@47.82 + account2 1400@39.80. Enter as single entry or blended.
- HKD→CNY = 0.92, USD→CNY = 7.0 (hardcoded, can override via env vars)
"""

import json
import sys
import os

HKD_TO_CNY = float(os.environ.get("HKD_TO_CNY", "0.92"))
USD_TO_CNY = float(os.environ.get("USD_TO_CNY", "7.0"))

def print_table(rows, headers, market):
    """Print a formatted table."""
    widths = [max(len(str(r[i])) for r in rows + [headers]) for i in range(len(headers))]
    
    # Header
    header_line = "| " + " | ".join(h.ljust(w) for h, w in zip(headers, widths)) + " |"
    sep = "|-" + "-|-".join("-" * w for w in widths) + "-|"
    print(header_line)
    print(sep)
    
    totals = {"mv": 0, "pl": 0, "cost": 0}
    for row in rows:
        line = "| " + " | ".join(str(r).ljust(w) if i > 0 else str(r).ljust(w) 
                                 for i, (r, w) in enumerate(zip(row, widths))) + " |"
        print(line)
    
    print()

def calc_hk(hk_data):
    """Calculate HK holdings P&L."""
    print("--- 港股 (HKD) ---")
    headers = ["名称", "持仓", "成本(HKD)", "现价(HKD)", "市值(HKD)", "盈亏(HKD)", "浮亏率"]
    rows = []
    total_mv = 0
    total_pl = 0
    total_cost = 0
    
    for h in hk_data:
        name = h["name"]
        shares = h["shares"]
        cost = h["cost"]
        price = h["price"]
        mv = shares * price
        pl = (price - cost) * shares
        pl_pct = (price - cost) / cost * 100
        rows.append([name, shares, f"{cost:.2f}", f"{price:.2f}", 
                     f"{mv:.0f}", f"{pl:+.0f}", f"{pl_pct:+.2f}%"])
        total_mv += mv
        total_pl += pl
        total_cost += shares * cost
    
    print_table(rows, headers, "hk")
    print(f"港股总市值: HKD {total_mv:,.0f}")
    print(f"港股总浮动盈亏: HKD {total_pl:+,.0f}")
    print(f"港股总成本: HKD {total_cost:,.0f}")
    print(f"港股浮亏率: {total_pl/total_cost*100:+.2f}%" if total_cost else "")
    print()
    return total_mv, total_pl

def calc_us(us_data):
    """Calculate US holdings P&L."""
    print("--- 美股 (USD) ---")
    headers = ["名称", "持仓", "成本(USD)", "现价(USD)", "市值(USD)", "盈亏(USD)", "浮亏率"]
    rows = []
    total_mv = 0
    total_pl = 0
    total_cost = 0
    
    for u in us_data:
        name = u["name"]
        shares = u["shares"]
        cost = u["cost"]
        price = u["price"]
        mv = shares * price
        pl = (price - cost) * shares
        pl_pct = (price - cost) / cost * 100
        rows.append([name, shares, f"{cost:.2f}", f"{price:.2f}", 
                     f"{mv:.0f}", f"{pl:+.0f}", f"{pl_pct:+.2f}%"])
        total_mv += mv
        total_pl += pl
        total_cost += shares * cost
    
    print_table(rows, headers, "us")
    print(f"美股总市值: USD {total_mv:,.0f}")
    print(f"美股总浮动盈亏: USD {total_pl:+,.0f}")
    print(f"美股总成本: USD {total_cost:,.0f}")
    print(f"美股浮亏率: {total_pl/total_cost*100:+.2f}%" if total_cost else "")
    print()
    return total_mv, total_pl

def calc_cn(cn_data):
    """Calculate A-Share holdings P&L."""
    print("--- A股 (RMB) ---")
    headers = ["名称", "持仓", "成本(RMB)", "现价(RMB)", "市值(RMB)", "盈亏(RMB)", "浮盈率"]
    rows = []
    total_mv = 0
    total_pl = 0
    total_cost = 0
    
    for c in cn_data:
        name = c["name"]
        shares = c["shares"]
        cost = c["cost"]
        price = c["price"]
        mv = shares * price
        pl = (price - cost) * shares
        pl_pct = (price - cost) / cost * 100
        rows.append([name, shares, f"{cost:.3f}", f"{price:.2f}", 
                     f"{mv:.0f}", f"{pl:+.0f}", f"{pl_pct:+.2f}%"])
        total_mv += mv
        total_pl += pl
        total_cost += shares * cost
    
    print_table(rows, headers, "cn")
    print(f"A股总市值: RMB {total_mv:,.0f}")
    print(f"A股总浮动盈亏: RMB {total_pl:+,.0f}")
    print(f"A股总成本: RMB {total_cost:,.0f}")
    print(f"A股浮盈率: {total_pl/total_cost*100:+.2f}%" if total_cost else "")
    print()
    return total_mv, total_pl

def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            data = json.load(f)
    else:
        raw = sys.stdin.read()
        if raw.strip():
            data = json.loads(raw)
        else:
            # Default: current verified holdings
            data = {
                "hk": [
                    {"name": "小米集团", "shares": 1600, "cost": 40.80, "price": 30.70},
                    {"name": "美团", "shares": 200, "cost": 98.83, "price": 82.70},
                    {"name": "蔚来", "shares": 200, "cost": 70.20, "price": 49.28},
                    {"name": "阿里巴巴", "shares": 200, "cost": 176.60, "price": 132.30},
                ],
                "us": [
                    {"name": "微软 MSFT", "shares": 8, "cost": 501.09, "price": 421.92},
                    {"name": "艺康 ECL", "shares": 18, "cost": 255.05, "price": 247.62},
                ],
                "cn": [
                    {"name": "美的集团", "shares": 1000, "cost": 69.886, "price": 82.57},
                    {"name": "比亚迪", "shares": 500, "cost": 101.771, "price": 96.30},
                    {"name": "300ETF", "shares": 5500, "cost": 4.571, "price": 4.878},
                    {"name": "AI智能ETF", "shares": 3700, "cost": 1.851, "price": 2.466},
                ]
            }
    
    print("=" * 60)
    print("九九 Portfolio P&L Calculator")
    print("=" * 60)
    print()
    
    hk_mv, hk_pl = calc_hk(data.get("hk", []))
    us_mv, us_pl = calc_us(data.get("us", []))
    cn_mv, cn_pl = calc_cn(data.get("cn", []))
    
    print("=" * 60)
    print("=== 汇总 (折合RMB) ===")
    print("=" * 60)
    
    total_rmb = hk_mv * HKD_TO_CNY + us_mv * USD_TO_CNY + cn_mv
    total_pl_rmb = hk_pl * HKD_TO_CNY + us_pl * USD_TO_CNY + cn_pl
    
    hk_cny = hk_mv * HKD_TO_CNY
    us_cny = us_mv * USD_TO_CNY
    
    print(f"港股折RMB: ¥{hk_cny:,.0f} ({hk_cny/total_rmb*100:.0f}%)")
    print(f"美股折RMB: ¥{us_cny:,.0f} ({us_cny/total_rmb*100:.0f}%)")
    print(f"A股: ¥{cn_mv:,.0f} ({cn_mv/total_rmb*100:.0f}%)")
    print(f"{'─' * 40}")
    print(f"总资产: ¥{total_rmb:,.0f}")
    print(f"总浮动盈亏: ¥{total_pl_rmb:+,.0f}")
    total_cost = total_rmb - total_pl_rmb
    print(f"总成本: ¥{total_cost:,.0f}")
    print(f"总盈亏率: {total_pl_rmb/total_cost*100:+.2f}%")
    print()

if __name__ == "__main__":
    main()
