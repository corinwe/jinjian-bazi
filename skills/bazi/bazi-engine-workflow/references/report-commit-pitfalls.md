# 报告推库两大坑（2026-09-29 实测）

## 坑① 同一个人多份报告 → SIG 只能对上一份
pre-commit 的产物溯源取 `/tmp/{姓名}_engine.json`（姓名来自**文件名前缀**）。
若同一人的 3 份报告（如小静 午/辰/子 三时辰）都跑同一姓名，`/tmp/小静_engine.json` 会被**最后一次运行覆盖**
→ 前两份报告内嵌 SIG 与现存的 JSON 不匹配 → 门禁 `⛔ 产物溯源失败`。

**解法（首选）**：每份跑完后立即留档 JSON，提交时逐份换上去：
```bash
cp /tmp/静_engine.json /tmp/静_engine_午时.json   # 每跑完一份就留档
git add <该份报告>; git commit
cp /tmp/静_engine_午时.json /tmp/静_engine.json    # 下一份提交前换回自己那份
```
即 **同一人 N 份 → 分 N 次提交**（每次只暂存该份报告）。

## 坑② 归档旧版必须让 git 认出「重命名」，否则被报告门禁拦
门禁用 `git diff --cached --diff-filter=ACM`：**R（重命名）不在内**。
所以 `git mv`/`git add -A` 让 git 识别为 R100 时 → 旧报告**免检直接归档**；
但若只 `git add <新文件>` 而旧文件用 `shutil.move` 移走，会变成 `D + ??`，一旦暂存
archive/ 里的旧报告就会以 **A（新增）** 身份进钩子 → 旧报告无【机制链注入】→ **拒推**。
**解法**：归档用 `git add -A <该人目录>`，确认 `git diff --cached --name-status` 显示 **R100** 再提交。

## 坑③ 别把别人的 WIP 一起 add
`git add -A <目录>` 会把同目录里其他会话未提交的改动一并暂存（本次：杨昌玉_v2.0_ALLNEW）。
**解法**：`git add -A <目录>` 后 `git reset -q -- <WIP文件>` 把它剔除；提交前用
`git diff --cached --name-status` 自检一遍。

## 坑④ SIG 必须在 postprocess 之后的最终 JSON 上算
`postprocess_dual_reports.py` 会重写 `/tmp/{name}_engine.json`（本次实证：它把 `best_da_yun` 清成 None）。
正确顺序：run_pipeline → postprocess → 机制链生成 → **SIG 在最终 JSON 上重算并对齐报告头**（已固化进 `scripts/build-single-report.py`）。
