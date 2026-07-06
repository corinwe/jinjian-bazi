# ═══════════════════════════════════════════════
# 金鉴真人·八字排盘平台 — 项目配置/凭据（技能引用副本·快速查）
# ═══════════════════════════════════════════════

## GitHub
- 仓库: corinwe/jinjian-bazi
- PAT: 存于 /root/bazi-platform/.hermes/config/credentials.md
- 推workflow需 `workflow` scope（当前PAT只有repo scope）
- PAT值获取: 读 credentials.md 或问老板

## 部署
- 路径: /root/bazi-platform/
- API: http://43.162.90.39:8000/
- 文档: http://43.162.90.39:8000/docs
- 启动: cd /root/bazi-platform && python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000

## SSH登录
- 服务器: root@43.162.90.39
- 密钥: ~/.ssh/id_ed25519.old（旧密钥，已授权）
- ❌ ~/.ssh/id_ed25519（当前密钥，未授权）

## 核心路径
- 引擎: /root/bazi-platform/engine/
- 排盘门禁: /root/bazi-platform/scripts/bazi-must-run-engine.sh
- 测试: /root/bazi-platform/engine/tests/
- 验证: cd /root/bazi-platform/engine/tests && python3 validate_all.py
- 前端: /root/bazi-platform/frontend/
- 知识库: /root/weiwuji-knowledge-base
- 人物档案: /root/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案/
- 人物档案编码: {序号}-{姓名}/（序号取目录最大号+1）

## 🔥 物理铁律（每次加载本文件时必须执行）

### 铁律① — 排盘必须跑引擎（禁止手算）
- 来源: 2026-06-29 梦的日柱算错教训；2026-07-04 全量审计修复
- 强制命令: `bash /root/bazi-platform/scripts/bazi-must-run-engine.sh -n <姓名> -g <性别> -y <年> -m <月> -d <日> -h <时>`
- 该脚本同时做两件事:
  1. `paipan.py get_full_paipan()` → 排盘（四柱八字）
  2. `pipeline_v5.py run_v5()` → 完整引擎评分（身强弱/财星/格局/喜用神/大运/流年/神煞/灾祸）
- 输出JSON含 `engine_scores` 字段
- 执行时机: 任何八字分析前先跑此脚本，禁止手算排盘或手算评分

### 铁律② — 知识库路径不依赖记忆
- 人物报告存放: /root/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案/{序号}-{姓名}/
- 编码规则: 序号为当前目录最大号+1
- GitHub: git@github.com:corinwe/weiwuji-knowledge-base.git
- 命令: `cd /root/weiwuji-knowledge-base && git add -A && git commit -m "消息" && git push`

### 铁律③ — 所有规则不能依赖LLM记忆
- 本文件是所有物理规则的单一来源
- 每次分析八字前，必须加载本文件（skill_view）
- 所有路径、命令、规则从这里读取，不靠回忆

### 铁律④ — 报告必须按标准格式输出（21§）
- 来源: bazi-report-template v5.2 标准模板
- 强制: 每次出报告前先加载 skill_view('bazi-report-template')
- 格式: 21§板块齐全，§1 25字段四段式，深度≥1,500行
- 禁止自创格式、禁止跳过模板直接输出

### 铁律⑤ — 大运年份必须校验（2026-07-01 大运起运年算错教训）
- 来源: 2026-07-01 家主丁亥30.4岁写成32-41岁，偏移1.6岁导致15年流年表全错
- 强制公式: **(结束年 - 开始年 + 1) 必须等于 10**
- 写大运前四步校验:
  1. **读数据源**: 从家族八字核心数据源_v1.json 精确提取起运年龄（不要凭印象写近似值）
  2. **算年份范围**: 起运年龄 + 10n = 第n+1运的结束年龄
  3. **交叉验证**: 大运干支必须与引擎排盘输出一致（阳男顺排/阴男逆排）
  4. **最终检查**: 每行大运的结束年-开始年+1 是否等于10
- 常见错误: 
  - ❌ 写2011~2021（12年）→ 应写2011~2020（10年）
  - ❌ 年龄区间凭印象（32-41）→ 应从数据源精确提取（30.4-40.4）
  - ❌ 子源(2011生·阴男)当前大运写庚寅 → 实际壬辰运（他才15岁）

### 铁律⑥ — 大运引擎节气天数必须自动计算（2026-07-05 硬编码1.1天教训）
- 来源: 2026-07-05 da_yun.py qi_yun_days=1.1硬编码导致主母/子源大运全错
- 强制: 调用 `compute_da_yun(bazi, birth_year, birth_month, birth_day)` 时必须传入birth_day
- qi_yun_days=None → 触发自动节气计算（基于compute_qi_yun_days + JIE_QI表）
- 禁用硬编码qi_yun_days=1.1——这个值只能在家主(1980-08-06,靠近立秋)碰对，对其他人都错

### 铁律⑦ — 大运引擎int截断检查（2026-07-05 int(0.37)=0教训）
- 来源: 2026-07-05 da_yun.py int(qi_yun_age)截断小数→所有大运年龄偏移
- 强制: 起运年龄全程浮点数，禁止int()截断
- 校验: 第一步大运start_age应等于qi_yun_age（如0.33），不是0
- DaYun.start_age/end_age 类型必须为 float（非 int）

### 铁律⑧ — 全量审计流程（2026-07-05 老板要求固化）
老板说「全量审计」时，依次执行:
1. **引擎模块审计**: da_yun.py→paipan.py→shen_qiang_ruo.py→ge_ju.py→shi_shen.py→constants.py
2. **脚本审计**: bazi-must-run-engine.sh参数传递、pipeline函数签名
3. **测试审计**: test_imports.py + validate_all.py
4. **大运验证**: 全家数据(家主/主母/子源)跑 compute_da_yun 验证
5. **报告对齐**: 生日/起运变更时更新知识库人物报告
6. **推库**: 全部修复后 git push

### 铁律⑨ — generate_deep_report 不依赖空paipan/basic_data（2026-07-05 固化）
- 来源: 2026-07-05 `report_generator.py` 第34行传空 `{"paipan":{}, "basic_data":{}, "result": result}` 给 `generate_deep_report`
- 禁用方案: `pp.get("year_pillar",{}).get("gan")` 或 `bd.get('month_pillar',{}).get('zhi','?')` 
- 强制: 改用 `_parse_bazi_str(bazi_str)` 从bazi字符串解析四柱干支
- bazi字符串在 `s1.get("bazi")` 中始终可用（来自引擎结果），比依赖 `pp`/`bd` 更可靠
- 核心技巧: `generate_deep_report.py` 中新增的 `_parse_bazi_str("庚申 癸未 辛亥 辛卯")` → `(庚,申,癸,未,辛,亥,辛,卯)`
- 验证: 直接用 `bazi_str` 构建 `BaZi(year=Pillar(yg,yz), month=Pillar(mg,mz), ...)` 计算五行能量
详见: `references/data-flow-field-name-audit-20260705.md`

### 铁律⑲ — 排盘源头自带藏干十神校验（2026-07-06 新增）
- bazi-must-run-engine.sh 执行时自动:
  1. 保存排盘JSON到 `/tmp/bazi_last_result.json`
  2. 调用 `python3 /root/bazi-platform/scripts/canggan-parse.py /tmp/bazi_last_result.json`
  3. 输出四柱每个地支的藏干、主气十神
  4. 标注「易混淆」项（辛+午=七杀⚠️）
- 来源: 2026-07-06 分析老板最佳时柱时午火=七杀误判为正官

### 铁律⑳ — 四柱分析结论5关校验（2026-07-06 新增）
- 命令: `python3 /root/bazi-platform/scripts/pillar-verify.py`
- 5关内容:
  1. 五鼠遁校验：候选时柱天干真实存在
  2. 藏干十神校验：易混淆项强制标注
  3. 结构优先级校验：三合局>单柱双喜
  4. 全局冲刑校验：新时柱冲了谁
  5. 最优性校验：是否有更好的候选被遗漏
- 来源: 2026-07-06 跨模型答案对比发现方法论缺陷

### 铁律㉑ — 分层加载机制（2026-07-06 更新）
两条独立线：
**系统级（自动加载）**：SOUL.md → profile根目录 · USER.md → memories · MEMORY.md → memories
**项目级（or链第1优先级）**：HERMES.md → 当前工作目录（取代AGENTS.md）
- skill内references/SOUL.md和references/USER.md为参考副本

## 测试命令速查
| 测试 | 命令 |
|:-----|:-----|
| 导入验证 | `cd engine && python3 tests/test_imports.py` |
| 全量测试(320条) | `cd engine && python3 tests/test_full_suite.py` |
| 覆盖率 | `python3 -m pytest engine/tests/test_full_suite.py --cov=engine --cov-fail-under=45` |
| E2E测试(16项) | `python3 engine/tests/test_e2e.py --remote` |
| 全量验证(26项) | `cd engine && python3 tests/validate_all.py` |
| **四柱校验(5关)** | **`python3 /root/bazi-platform/scripts/pillar-verify.py`** |
| 部署前检查 | 见HERMES.md |

## DevOps工具
| 工具 | 命令 |
|:-----|:-----|
| 一键加固 | `./setup-devops.sh`（`--check`查状态）|
| 一键回滚 | `./rollback.sh [commit|--list]` |
| 配置部署 | `./setup-deploy.sh` |
| 一键启动 | `./run.sh` |

## 项目结构
```
/root/bazi-platform/
├── engine/              # 规则引擎（44模块，已审计）
├── api/                 # FastAPI服务
├── frontend/            # 前端SPA
├── database/            # SQLite
├── docs/                # 文档
│   └── ci-cd.yml        # CI/CD workflow（需配workflow scope的PAT才能推）
├── .github/workflows/   # CI/CD配置（当前未推成功）
├── .pre-commit-config.yaml  # Git hooks
├── pyproject.toml       # ruff/pytest-cov/mypy/black配置
├── Dockerfile
├── run.sh               # 启动脚本
├── setup-devops.sh      # 一键加固脚本
├── setup-deploy.sh      # 部署配置助手
├── rollback.sh          # 回滚脚本
└── .hermes/config/credentials.md  # 完整凭据
```
