#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pre_tool_call hook — 物理拦截层 v2.0（2026-09-10 双引擎升级）
==============================================================
在 write_file/patch 执行前拦截报告类写入，强制满足**双引擎数据源**要求：

  默认（无豁免标记）：必须同时具备
    ① BAZI_DATASOURCE 环境变量 + 文件存在
    ② /tmp/{姓名}_ziwei.json 存在（紫微·第四引擎）
    ③ 紫微引擎四柱交叉校验 == 八字引擎四柱（一致才放行）
    ④ /tmp/.bazi_verified 已 touch（人工/脚本验证通过）

  豁免（仅老板明确说明时才允许创建）：
    /tmp/.bazi_only  → 只用传统八字，不需紫微
    /tmp/.ziwei_only → 只用紫微，不需八字

  放行后消费掉 /tmp/.bazi_verified（一次一用，防止跳过门禁）。
"""
import sys, json, os, re

VERIFY_FLAG = "/tmp/.bazi_verified"
BAZI_ONLY_FLAG = "/tmp/.bazi_only"
ZIWEI_ONLY_FLAG = "/tmp/.ziwei_only"

REPORT_KEYWORDS = ["报告", "分析", "report", "analysis"]


def _mode() -> str:
    if os.path.exists(BAZI_ONLY_FLAG):
        return "bazi"
    if os.path.exists(ZIWEI_ONLY_FLAG):
        return "ziwei"
    return "dual"


def _block(msg: str):
    print(json.dumps({"action": "block", "message": msg}, ensure_ascii=False))


def _extract_name(filepath: str, ds_path: str) -> str:
    """从报告文件名或数据源文件名提取姓名"""
    base = os.path.basename(filepath)
    m = re.match(r"^(.+?)[_\-](报告|分析|report|analysis)", base)
    if m:
        return m.group(1)
    # 退而求其次：从 ds 路径取
    if ds_path:
        b = os.path.basename(ds_path)
        m2 = re.match(r"^(.+?)_(ds|engine|ziwei)\.json$", b)
        if m2:
            return m2.group(1)
    return ""


def _ziwei_check(name: str):
    """返回 (ok, msg)"""
    cands = [f"/tmp/{name}_ziwei.json"] if name else []
    if not cands or not os.path.exists(cands[0]):
        # 兜底：/tmp 下唯一一个 _ziwei.json
        import glob
        g = glob.glob("/tmp/*_ziwei.json")
        if len(g) == 1:
            cands = g
        else:
            return False, (
                f"⛔ 物理拦截【双引擎门禁】：未找到紫微数据源。\n"
                f"  期望文件: /tmp/{name or '{姓名}'}_ziwei.json\n"
                f"  请执行: bash projects/bazi-platform/scripts/bazi-dual-prepare.sh {name or '<姓名>'} <性别> <YYYY-MM-DD> <HH:MM> [出生地]\n"
                f"  ─────────────────────────────────────────\n"
                f"  【默认铁律】任何八字评估必须 八字×紫微 双引擎合参。\n"
                f"  仅当老板明确说「只用八字」→ 运行加 --bazi-only\n"
                f"  仅当老板明确说「只用紫微」→ 运行加 --ziwei-only"
            )
    try:
        d = json.load(open(cands[0], encoding="utf-8"))
    except Exception as e:
        return False, f"⛔ 物理拦截：紫微数据源 {cands[0]} 解析失败: {e}"
    cv = d.get("四柱交叉校验") or {}
    if not cv.get("一致"):
        return False, (
            f"⛔ 物理拦截【双引擎不一致】：紫微={cv.get('紫微引擎')} 八字={cv.get('八字引擎')}\n"
            f"  双引擎四柱必须一致才可出报告（这是防止源头数据错误的最后一道闸）。\n"
            f"  请先执行: python3 projects/bazi-platform/scripts/bazi-jieqi-regression.py --quick\n"
            f"  定位 engine/jieqi.py 节气定界问题后重跑 bazi-dual-prepare.sh。"
        )
    return True, f"✅ 紫微数据源就绪（{d.get('紫微', {}).get('五行局')}·命主{d.get('紫微', {}).get('命主')}）"


def main():
    raw = sys.stdin.read()
    # 🚨 2026-09-10 调试：记录真实 payload（用于核对字段名，确认门禁是否真的生效）
    try:
        with open("/tmp/hook_raw_payload.json", "w", encoding="utf-8") as _f:
            _f.write(raw[:20000])
    except Exception:
        pass
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return  # 非JSON，放行

    tool_name = payload.get("tool_name", "") or payload.get("tool", "") or payload.get("name", "")
    args = payload.get("args", None)
    if args is None:
        for k in ("tool_args", "arguments", "parameters", "input", "params", "tool_input"):
            if isinstance(payload.get(k), dict):
                args = payload[k]
                break
    args = args or {}

    if tool_name not in ("write_file", "patch"):
        return

    filepath = args.get("path", "") or ""
    if not filepath.endswith(".md"):
        return
    # 🚨 收窄报告识别（2026-09-10 v2.1）：避免误伤技能/文档文件
    #   旧逻辑 `any(kw in path for kw in ["报告","分析","report","analysis"])` 会把
    #   skills/bazi/bazi-wealth-analysis/SKILL.md 之类也当成报告拦截 → 误伤。
    #   真报告判定：路径含「报告/report」，或在报告输出目录下且含分析类词。
    lp = filepath.lower()
    REPORT_DIRS = ["/tmp/", "人物档案", "/reports/", "/output/", "\\reports\\"]
    is_report = ("报告" in filepath) or ("report" in lp) or (
        any(kw in filepath or kw in lp for kw in ["分析", "analysis"]) and any(d in filepath for d in REPORT_DIRS)
    )
    if not is_report:
        return

    mode = _mode()
    ds_path = os.environ.get("BAZI_DATASOURCE", "")
    name = _extract_name(filepath, ds_path)

    # ── 八字侧门禁（dual / bazi 模式）──
    if mode in ("dual", "bazi"):
        if not ds_path:
            _block(
                "⛔ 物理拦截：BAZI_DATASOURCE 环境变量未设置。\n"
                "  正确流程（双引擎默认）：\n"
                "  bash projects/bazi-platform/scripts/bazi-dual-prepare.sh <姓名> <性别> <YYYY-MM-DD> <HH:MM> [出生地]\n"
                "  该脚本会同时产出 八字数据源 + 紫微数据源，并做四柱交叉校验。"
            )
            return
        if not os.path.exists(ds_path):
            _block(
                f"⛔ 物理拦截：BAZI_DATASOURCE={ds_path} 文件不存在。\n"
                f"  请执行: bash projects/bazi-platform/scripts/bazi-dual-prepare.sh {name or '<姓名>'} <性别> <YYYY-MM-DD> <HH:MM>"
            )
            return

    # ── 紫微侧门禁（dual / ziwei 模式）──
    if mode in ("dual", "ziwei"):
        ok, msg = _ziwei_check(name)
        if not ok:
            _block(msg)
            return

    # ── 验证标记门禁 ──
    if os.path.exists(VERIFY_FLAG):
        os.remove(VERIFY_FLAG)  # 一次验证只用一次
        return

    mode_label = {"dual": "八字×紫微双引擎", "bazi": "只用传统八字(豁免)", "ziwei": "只用紫微(豁免)"}[mode]
    _block(
        f"⛔ 物理拦截：写入 {filepath} 前未通过验证。\n"
        f"  当前模式: {mode_label}\n"
        f"  请先完成数据源校验，然后执行：touch {VERIFY_FLAG}\n"
        f"  标准流程:\n"
        f"    bash projects/bazi-platform/scripts/bazi-dual-prepare.sh {name or '<姓名>'} <性别> <YYYY-MM-DD> <HH:MM>\n"
        f"    touch {VERIFY_FLAG}\n"
        f"  （若老板明确要求只跑单引擎，在 prepare 脚本后加 --bazi-only 或 --ziwei-only）"
    )


if __name__ == "__main__":
    main()
