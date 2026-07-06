# 约束系统实战踩坑录（2026-06-24）

> 本会话中构建约束系统时发现的23个已修复bug。
> 坑①~⑩：约束系统构建/配置时的bug
> 坑⑪~⑮：bazi-full-verify.sh / bazi-must-verify.sh 脚本bug（2026-06-24完整排盘测试发现）
> 坑⑯~⑲：前15个bug中遗漏的trim/年干/年份取整等bug
> 坑⑳~㉓：本会话完整排盘测试发现的追加bug

## 坑① — precheck.sh `grep -q | grep -vq` pipe条件永假

```bash
# ❌ 错误（pipe无声问题）
if echo "$CMD" | grep -qi "bazi" | grep -vqi "pipeline"; then
  # grep -q 抑制stdout → pipe传给第二个grep的是空输入 → 第二个grep永远返回false
fi

# ✅ 正确（用 && 替代 pipe）
if echo "$CMD" | grep -qi "bazi" && ! echo "$CMD" | grep -qi "pipeline"; then
  echo "✅ 正确逻辑"
fi
```

## 坑② — 插件代码的CLI参数必须与实际pipeline.sh一致

写plugin时假设pipeline接受 `--birth "1990-05-15"` 和 `--output /tmp/out.json`，但实际pipeline用 `--year/--month/--day` 且无 `--output` 参数。还缺 `--gender`（必填）。

```bash
# pipeline.sh 实际CLI（2026-06-24确认）
bash bazi-pipeline.sh --name {姓名} --gender {男/女} \
  --year {年} --month {月} --day {日} \
  --hour {时} --min {分} --hour-idx {索引}

# ❌ 不存在：--birth, --output
# ❌ gender必填（用户原文代码缺gender！）
```

**强制流程**：每次写pipeline wrapper/plugin前，先 `head -60 pipeline.sh` 确认CLI。禁止凭记忆。

## 坑③ — handler.py 与 shell hooks 的 pre_tool_call 双重拦截

Python handler.py 和 shell precheck.sh 都在 pre_tool_call 事件上注册了拦截逻辑。设计意图是 defense-in-depth：shell钩子拦截明文命令，Python钩子拦截Hermes工具级调用。

如果发现双钩子导致操作异常，可配置config.yaml只启用其中一个。

## 坑④ — SOUL.md vs AGENTS.md 覆盖范围差异

| 特性 | SOUL.md（人格宪法） | AGENTS.md（项目规则） |
|:----|:-------------------|:---------------------|
| 加载机制 | 写入系统提示词 | 仅当cron workdir指向知识库时 |
| 可绕过性 | ❌ 极难 | ⚠️ 容易 |
| 规则量 | 10条铁律 | B/C/D三组20+标准 |

重要约束必须放SOUL.md。AGENTS.md只适合放参考性规则。

## 坑⑤ — 两处数据源可能不同步

- pipeline.sh 读：`${SCRIPT_DIR}/family_bazi_data.json`
- 约束系统引用：`知识库/.../家族八字核心数据源_v1.json`

更新数据时必须两处都更新。

## 坑⑥ — 约束生效范围与profile的关系

| 配置项 | 所属profile | 生效范围 |
|:------|:-----------|:---------|
| config.yaml | jinjian-zhenren | 当前会话 |
| SOUL.md | jinjian-zhenren | 当前会话 |
| AGENTS.md | weiwuji-knowledge-base | 仅当workdir指向 |
| hooks/ | default | 所有profile |
| plugins/ | default → B配置级修正 | 用户选了配置级专属 |

## 坑⑦ — write_file工具受cross-profile guard限制 / profile迁移

写入default profile的plugins/、hooks/目录时，write_file被cross-profile guard拦截。

**用户最终选择**：B配置级（`/root/.hermes/profiles/jinjian-zhenren/plugins/`），非default profile。

```bash
# 迁移命令
mkdir -p ~/.hermes/profiles/jinjian-zhenren/plugins/bazi-enforcer/
cp ~/.hermes/plugins/bazi-enforcer/* ~/.hermes/profiles/jinjian-zhenren/plugins/bazi-enforcer/
rm -rf ~/.hermes/plugins/bazi-enforcer/
```

**lesson**：首次创建plugin时，直接使用配置级路径，避免迁移。

## 坑⑧ — handler.py tool_name 不兼容不同Hermes版本

**表现**：handler.py 的 `_pre_tool_check` 检查 `tool_name == "execute_command"`，但不同Hermes版本或不同provider下terminal工具可能注册为 `"terminal"`、`"execute_bash"`、`"run_shell"`、`"bash"` 等不同名称。

**修复 v2.0**：
```python
TOOL_NAMES_TERMINAL = {"terminal", "execute_command", "execute_bash", "run_shell", "bash"}
is_terminal = tool_name in TOOL_NAMES_TERMINAL
```
同时检查 `params.command` 和 `context.command` 多个可能的数据源。

## 坑⑨ — check.sh 只支持 .json，不支持 .md 报告校验

**表现**：原始 check.sh 只检查 JSON 文件的 `PIPELINE-SIG` 签名和 `jq` 字段，但实际bazi报告是 .md 格式，需要调 `bazi-format-check.py` 和 `bazi-report-validator.py`。

**修复 v2.0**：按文件扩展名分支：
```bash
if [[ "$EXT" == "md" ]]; then
  # .md报告：检查签名 → 调format-check.py → 调report-validator.py
elif [[ "$EXT" == "json" ]]; then
  # .json文件：签名 + jq字段校验
else
  # 其他：仅检查SIG存在
fi
```

## 坑⑩ — precheck.sh 未拦截直接访问skills目录绕过pipeline

**表现**：Agent可以通过 `cat /root/bazi-platform/skills/bazi-*/references/*.md` 直接从skills目录读取数据，绕过pipeline的数据源头盔机制。

**修复**：在 precheck.sh 加两条拦截规则：
```bash
# 禁止直接读skills数据
if echo "$COMMAND" | grep -q "$BAZI_SKILLS_DIR" && ! echo "$COMMAND" | grep -qi "pipeline"; then
  echo "❌ 禁止绕过pipeline直接读取技能数据"; exit 1
fi
# 禁止直接跑bazi脚本
if echo "$COMMAND" | grep -q "$BAZI_SCRIPTS_DIR" && ! echo "$COMMAND" | grep -qi "pipeline"; then
  if echo "$COMMAND" | grep -qiE '(bazi-engine|bazi-gate|bazi-must-verify)'; then
    echo "❌ 禁止绕过pipeline直接运行排盘脚本"; exit 1
  fi
fi
```

## 坑⑪ — bazi-full-verify.sh check() 函数判定逻辑颠倒

**表现**：check() 函数用 `[ "$result" -eq 0 ]` 作为通过条件。当 `grep -c "补财库"` 返回 "5"（5处匹配）时，`5 -eq 0` 为 false → 判定为 FAIL！正确逻辑应该是 `≥1` 表示匹配项存在。

```bash
# ❌ 旧的check函数（计数返回的判定逻辑颠倒）
check() {
    if [ "$result" = "true" ] || [ "$result" = "0" ] || [ "$result" -eq 0 ] 2>/dev/null; then
        # 把"找到了5处匹配"判定为FAIL ❌
    fi
}

# ✅ 修复后的check函数
check() {
    result=$(echo "$result" | tr -d '\n\r ')  # 先trim换行
    if [ "$result" = "true" ] || { [ "$result" -ge 1 ] 2>/dev/null; }; then
        # "找到了5处匹配" → 5≥1 → PASS ✅
    fi
}
```

**修改位置**：`bazi-full-verify.sh` L39-51

## 坑⑫ — bazi-full-verify.sh 旧§板块名称硬编码

**表现**：full-verify.sh 使用硬编码的§板块名数组检查报告完整性（`"§2 格局分析" "§3 身强弱"`等），但AGENTS.md标准命名不同（`§2 命盘排布`），且子agent实际使用的命名又不同。三者不一致导致所有§板块被报告为"缺失"。

**修复**：改为按§编号扫描（`grep -c "§N[^0-9]"`），不依赖具体名称，支持灵活命名。同时兼容 `§X. `格式。

**修改位置**：`bazi-full-verify.sh` L121-130

## 坑⑬ — BIRTH_YEAR 提取匹配到报告日期而非出生年

**表现**：`grep -oP '19[0-9]{2}|20[0-9]{2}'` 从报告全文提取的第一个4位数是 "2026"（报告编制日期），而非出生年 "1980"。导致文昌检查逻辑误入IF分支。

**修复**：限定从公历出生行提取：`grep -oP '公历1\d{3}|公历2\d{3}'`

**修改位置**：`bazi-full-verify.sh` L168

## 坑⑭ — 关键年份标签使用【】括号而非[]括号

**表现**：full-verify.sh `check("关键年份类型标记")` 用 `\[学业\]` (方括号) 搜索，但子agent报告实际使用 `【学业】`。0匹配导致FAIL。

**修复**：改成搜索 `【学业】` 格式。AGENTS.md B5 统一以【】为准。

## 坑⑮ — bazi-must-verify.sh §1表格 L200-201 硬编码日主/性别

**表现**：`bazi-must-verify.sh` 的§1表格输出（L200-201）使用硬编码字符串：
```bash
echo "| 3 | **日主** | ${ENGINE_RIZHU}土（阴土） |"    # ❌ 永远输出"土"
echo "| 4 | **性别** | 女（阳女逆排·配偶星=正官/七杀） |"  # ❌ 永远输出"女"
```
而该文件头部元数据输出（L178/L188）已正确使用了动态变量。

**修复**：改为使用已在L169-187计算好的 `RZ_WX/RZ_TYPE/GENDER/PAIXIANG/PEIOU` 变量。

**5个must-verify.sh bug汇总**：

| Bug | 位置 | 发现时间 | 已修? |
|:----|:----|:---------|:-----:|
| 性别参数传数字而非中文 | L56传入→引擎 | 2026-06-23 | ✅ |
| 日主五行写死为"土"（头部） | L168 | 2026-06-23 | ✅ |
| 性别写死为"女"（头部） | L169 | 2026-06-23 | ✅ |
| **日主写死为"土"（§1表格）** | **L200** | **2026-06-24** | **✅** |
| **性别写死为"女"（§1表格）** | **L201** | **2026-06-24** | **✅** |

## 坑⑯ — full-verify.sh 多变量未trim换行导致 integer expression expected

**表现**：`KG_COUNT` 和 `JL_COUNT` 变量直接用整数比较。`$(grep -c ... || echo 0)` 可能包含换行符。

**修复**：所有grep输出加 `tr -d '\n\r '` 消除换行，变量引用加引号，比较加 `2>/dev/null`。

## 坑⑰ — bazi-engine.py end_year 公式多+10（已修复）

**表现**：大运年份显示为1980~1999（19年跨度），正确的10年应显示为1980~1989。

**根因**：`bazi-engine.py` line 783：
```python
# ❌ 错误
end_year = b_year + int(end_age + 10) - 1  # → 1980+20-1=1999（19年）
# ✅ 正确
end_year = b_year + int(end_age) - 1        # → 1980+10-1=1989（10年 ✅）
```

## 坑⑱ — bazi-engine.py 大运年份取整算法两次修正（2026-06-24）

第一次修正：加year_offset（中间方案·已废弃）
第二次修正：完全重写，用起运实际年份做基数（最终方案·当前有效）

**中间方案（已废弃）**：加 `year_offset` 逻辑——起运在7月以后年份+1。
问题：month ≥ 7 阈值不准，且 `b_year + int(start_age) + offset` 对大起运年龄（8岁/9岁）也不准。

**最终方案（当前有效·2026-06-24）**：完全废弃 `b_year + int(age)` 路线，直接用起运实际开始年份做基数。

```python
# ✅ 最终算法
from datetime import timedelta
qi_yun_start = result['birth'] + timedelta(days=qi_yun_age * 365.25)
qi_yun_start_year = qi_yun_start.year
# 起运在Q4(10~12月) → 进位到下一年
if qi_yun_start.month >= 10:
    qi_yun_start_year += 1

for i, dy in enumerate(da_yun_list):
    start_year = qi_yun_start_year + i * 10
    end_year = start_year + 9
```

## 坑⑲ — must-verify.sh 性别参数只认0/1不认男/女（已修复）

```bash
# ❌ 原始
GENDER="男"; [ "$SEX" = "0" ] && GENDER="女"

# ✅ 修复
GENDER="男"
if [ "$SEX" = "0" ] || [ "$SEX" = "女" ]; then
    GENDER="女"
fi
```

## 坑⑳ — must-verify.sh 起运方向用日主阴阳，应为年干（严重级）

**发现**：刘成（丁卯年·丁=阴·女）→ must-verify.sh 输出「阳女逆排」，正确应为「阴女顺排」。

**根因**：must-verify.sh L185 用 `$ENGINE_RIZHU`（日主干支）判阴阳，但起运方向取决于**年干**阴阳。

```bash
# ❌ 错误：用日主
YIN_YANG=$(echo "$ENGINE_RIZHU" | grep -q '[乙丁己辛癸]' && echo "阴" || echo "阳")

# ✅ 正确：用年干
Y_GAN=$(echo "$ENGINE_BAZI" | awk '{print substr($1,1,1)}')
YIN_YANG=$(echo "$Y_GAN" | grep -q '[乙丁己辛癸]' && echo "阴" || echo "阳")
```

**影响范围**：所有「日主阴阳≠年干阴阳」的八字。engine本身的起运方向是正确（用年干），仅限于 must-verify.sh 的标签展示。

---

## 坑㉔ — git checkout 清除未提交的大文件改动（2026-06-27·generate_deep_report.py教训）

**表现**：`generate_deep_report.py` 从500行逐步扩展到1730行（82K），期间多次`patch`和`write_file`。当执行 `git checkout generate_deep_report.py` 试图恢复某次patch破坏的版本时，整个文件被清空为0字节——所有累加的改动全部丢失。

**根因**：`git checkout` 会：
1. 用最近一次`git commit`的版本覆盖工作目录中的文件
2. 如果文件从未被`git commit`过（用`write_file`新创建后还没有`git add`+`git commit`），`git checkout`会删除文件或清空
3. `patch`工具的多重改动、`write_file`的大文件、`git checkout`的恢复操作三者在大型文件上容易冲突

**防御措施**：
```bash
# 1. 在git checkout前，先把当前改动保存到临时文件
cp generate_deep_report.py /tmp/backup_gdr_latest.py

# 2. 或者先用git stash暂存
git stash push -m "正在进行的大文件改动" generate_deep_report.py

# 3. 检查文件是否在git历史中
git log --oneline generate_deep_report.py  # 有输出→有历史；NO output→从未提交过

# 4. 对从未提交过的大文件（>50K），用cp备份而非git checkout恢复
```

**教训（2026-06-27总结）**：
- 大文件（>50K）的修改过程中，务必定期`git add`+`git commit`（即使是不完整的中间版本）
- `write_file`创建的大Python文件在git commit前是「流浪文件」——`git checkout`可以无声无息地杀死它
- 恢复代码错误的正确流程：`cp /tmp/backup.py target.py` 优于 `git checkout target.py`
- 本会话丢失了约50次patch的历史（约82K代码），最终靠`write_file`重新生成全集

修完23个bug后，6人引擎+官网双验证，全部一致：

| 姓名 | 八字 | 日主 | 身强弱 | 起运 | 首大运 | 状态 |
|:----|:-----|:----:|:------:|:----:|:------|:----:|
| 魏启令(家主) | 庚申癸未辛亥辛卯 | 辛金 | 64.0分 身强 | 0岁4月 | 甲申 1981~1990 | ✅ |
| 魏源(子源) | 辛卯癸巳丙戌癸巳 | 丙火 | 55.6分 中和 | 8岁6月 | 壬辰 2020~2029 | ✅ |
| 刘成(主母) | 丁卯丁未庚午壬午 | 庚金 | 50.0分 从弱 | 6岁2月 | 戊申 1993~2002 | ✅ |
| 杨胜源 | 庚寅乙酉戊寅丁巳 | 戊土 | 12.0分 身弱 | 4岁3月 | 丙戌 2015~2024 | ✅ |
| 朱宗立(立) | 辛卯癸巳甲戌庚午 | 甲木 | 4.0分 身弱 | 4岁6月 | 壬辰 2016~2025 | ✅ |
| 张法英 | 壬辰戊申癸卯癸丑 | 癸水 | 92.4分 身强 | 5岁9月 | 丁未 1958~1967 | ✅ |

**结论**：2026-06-24 全量修复后，引擎正确性、验证体系、约束系统三层均通过6人端到端测试。
