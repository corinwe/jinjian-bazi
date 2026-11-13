#!/usr/bin/env bash
# ============================================================
# P0 端到端验证（一命令跑全部）
#   1. 黄金盘回归 12 例
#   2. 自刑判定回归 12 例
#   3. 紫微门禁 12 条
#   4. 起运口径回归
#   5. 节气定界回归
#   6. 上下文清单校验
#   7. 轨迹回放（≥5 决策点）
#   8. 报告质量门禁（优先 /tmp/少爷_报告_双引擎.md，回退 21§ 版）
# 退出码：0=全部通过；1=有失败
# ============================================================
set -u
cd "$(dirname "$0")/.." || exit 1

PASS=0; FAIL=0; SKIP=0
declare -a LINES

run() {
  local name="$1"; shift
  local out code
  out=$("$@" 2>&1); code=$?
  if [ $code -eq 0 ]; then
    PASS=$((PASS+1)); LINES+=("✅ ${name}")
    echo "✅ ${name}"
  else
    FAIL=$((FAIL+1)); LINES+=("❌ ${name} (exit ${code})")
    echo "❌ ${name} (exit ${code})"
    echo "${out}" | tail -12 | sed 's/^/     /'
  fi
}

echo "══════════ P0 端到端验证 ══════════"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "目录: $(pwd)"
echo

run "黄金盘回归（12 例）"      python3 scripts/regression-golden.py
run "自刑判定回归（12 例）"    python3 engine/tests/test_xing_chong_he_hua.py
run "紫微门禁（12 条）"        python3 engine/ziwei_gates.py --fast
run "起运口径回归"             python3 scripts/bazi-qiyun-regression.py
run "节气定界回归"             python3 scripts/bazi-jieqi-regression.py
run "上下文清单校验"           python3 scripts/context-manifest-check.py
run "轨迹回放（≥5 决策点）"    python3 scripts/trace-replay.py

REPORT_CHECK="/tmp/少爷_报告_双引擎.md"
if [ -f "$REPORT_CHECK" ]; then
  run "报告质量门禁（少爷 双引擎全量版）" python3 /root/.hermes/profiles/jinjian-zhenren/scripts/verify-report-quality.py "$REPORT_CHECK"
elif [ -f /tmp/少爷_report.md ]; then
  run "报告质量门禁（少爷 21§引擎版）" python3 /root/.hermes/profiles/jinjian-zhenren/scripts/verify-report-quality.py /tmp/少爷_report.md
else
  SKIP=$((SKIP+1)); LINES+=("⏭  报告质量门禁（跳过：无报告产物）")
  echo "⏭  报告质量门禁（跳过：无报告产物）"
fi

echo
echo "══════════ 汇总 ══════════"
for l in "${LINES[@]}"; do echo "$l"; done
echo "──────────────────────────"
echo "通过 ${PASS} / 失败 ${FAIL} / 跳过 ${SKIP}"
if [ ${FAIL} -gt 0 ]; then
  echo "⛔ P0 验证未通过"
  exit 1
fi
echo "✅ P0 端到端验证全部通过"
exit 0
