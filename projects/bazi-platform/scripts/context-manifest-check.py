#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""上下文清单校验（P0-3）

作用：
  1. 校验 .hermes/context-manifest.yaml 的钉住事实与引擎数据源一致；
  2. 压缩/重启后，用 --emit 把钉住事实重新注入上下文；
  3. 任一不一致 → exit 1（防止"记错生日/记错四柱"这类致命错误）。

用法：
    python3 scripts/context-manifest-check.py            # 校验
    python3 scripts/context-manifest-check.py --emit     # 打印可注入的钉住事实
    python3 scripts/context-manifest-check.py --strict   # 数据源缺失也算失败
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / ".hermes" / "context-manifest.yaml"


def get_path(obj, dotted: str):
    cur = obj
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit():
            cur = cur[int(part)]
        else:
            raise KeyError(part)
    return cur


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    if not MANIFEST.exists():
        print(f"⛔ 缺少上下文清单: {MANIFEST}")
        return 1

    m = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    facts = m.get("pinned_facts", [])
    pin_keys = set(m.get("compaction", {}).get("pin_keys", []))

    if args.emit:
        print("【钉住事实·压缩后必须保留】")
        for f in facts:
            if f["key"] in pin_keys:
                print(f"- {f['key']}：{f['value']}" + (f"（{f['note']}）" if f.get("note") else ""))
        return 0

    failures, warnings = [], []
    defined = {f["key"] for f in facts}
    for k in sorted(pin_keys - defined):
        failures.append(f"pin_keys 中 '{k}' 未在 pinned_facts 定义")

    print(f"{'结果':<4}{'钉住事实':<12}{'期望值':<34}校验")
    print("─" * 78)
    for f in facts:
        key, exp = f["key"], f["value"]
        src, path = f.get("source"), f.get("path")
        status = "✅ 自检通过"
        if src:
            p = Path(src)
            if not p.exists():
                status = "⚠️ 数据源缺失"
                if f.get("required_source") or args.strict:
                    failures.append(f"{key}: 数据源不存在 {src}")
                else:
                    warnings.append(f"{key}: 数据源不存在 {src}")
            else:
                try:
                    if str(p).endswith(".json"):
                        data = json.loads(p.read_text(encoding="utf-8"))
                    else:
                        data = p.read_text(encoding="utf-8")
                    if path:
                        actual = get_path(data, path)
                    else:
                        actual = data
                    if f.get("contains"):
                        ok = f["contains"] in (actual if isinstance(actual, (list, str)) else str(actual))
                    else:
                        ok = (actual == exp) or (str(actual) == str(exp))
                    status = "✅ 一致" if ok else f"❌ 不一致→实际 {str(actual)[:80]}"
                    if not ok:
                        failures.append(f"{key}: 期望 {exp} / 实际 {str(actual)[:80]}")
                except Exception as e:  # noqa: BLE001
                    status = f"❌ 读取失败 {type(e).__name__}"
                    failures.append(f"{key}: 读取 {src}#{path} 失败: {e}")
        print(f"{'OK' if status.startswith('✅') else 'FAIL':<4}{key:<12}{str(exp)[:32]:<34}{status}")

    print()
    if warnings:
        for w in warnings:
            print(f"⚠️  {w}")
    if failures:
        for e in failures:
            print(f"❌ {e}")
        print(f"\n⛔ 上下文清单校验失败（{len(failures)} 项）")
        return 1
    print(f"✅ 上下文清单校验通过（{len(facts)} 条钉住事实）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
