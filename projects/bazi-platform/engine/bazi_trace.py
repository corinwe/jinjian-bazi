#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""轻量轨迹记录器（P0-2）

设计目标：
1. 每次排盘/报告生成，落一条可回放的决策轨迹（JSONL）。
2. 零外部依赖、零行为改变（默认只写文件，不改任何计算结果）。
3. 文件位置：<project>/runs/<run_id>/trace.jsonl

用法：
    from bazi_trace import Tracer
    t = Tracer("主母_20261030_120000", meta={"name": "主母"})
    t.log("paipan", result={"四柱": "丁卯 丁未 庚午 壬午"})
    t.log("ge_ju", result={"main": "从弱格"})
    t.close(summary={"ok": True})

环境变量：
    BAZI_TRACE=0        关闭轨迹（默认开启）
    BAZI_TRACE_DIR=...  自定义轨迹根目录
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

_DEFAULT_ROOT = Path(__file__).resolve().parent.parent / "runs"
TRACE_ROOT = Path(os.environ.get("BAZI_TRACE_DIR", str(_DEFAULT_ROOT)))


def enabled() -> bool:
    return os.environ.get("BAZI_TRACE", "1") not in ("0", "false", "False", "")


def digest(obj: Any) -> str:
    """对任意对象做稳定摘要（用于比对输入/输出是否变化）。"""
    try:
        raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str)
    except Exception:
        raw = repr(obj)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


class Tracer:
    def __init__(self, run_id: str, meta: dict | None = None, root: Path | None = None):
        self.run_id = run_id
        self.root = Path(root) if root else TRACE_ROOT
        self.dir = self.root / run_id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / "trace.jsonl"
        self.seq = 0
        self.t0 = time.time()
        self._write({"event": "start", "meta": meta or {}})

    def _write(self, rec: dict) -> None:
        rec = {
            "seq": self.seq,
            "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "elapsed_ms": round((time.time() - self.t0) * 1000, 1),
            **rec,
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
        self.seq += 1

    def log(self, step: str, **fields: Any) -> None:
        """记录一个决策点。约定字段：input/output/result/note/gate/artifact。"""
        rec: dict[str, Any] = {"event": "step", "step": step}
        for k, v in fields.items():
            rec[k] = v
            if k in ("input", "inputs", "output", "outputs", "result", "artifact"):
                rec[f"{k}_digest"] = digest(v)
        self._write(rec)

    def close(self, summary: dict | None = None) -> None:
        self._write({"event": "end", "summary": summary or {}, "total_steps": self.seq})


def latest_run(root: Path | None = None) -> str | None:
    root = Path(root) if root else TRACE_ROOT
    if not root.exists():
        return None
    runs = [p for p in root.iterdir() if p.is_dir() and (p / "trace.jsonl").exists()]
    if not runs:
        return None
    return max(runs, key=lambda p: p.stat().st_mtime).name
