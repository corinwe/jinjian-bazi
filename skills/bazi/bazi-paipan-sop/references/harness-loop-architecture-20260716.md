# Harness Engine x Loop Engineering 架构（2026-07-16 session完整建设）

## 架构概览

```
Agent = Model + Harness

Harness = Everything outside the model:
  ① Workflow (确定性编排) — YAML/Python定义Phase 0-6
  ② Guides (前馈) — BAZI_DATASOURCE, rules/*.yaml, templates/*.md
  ③ Sensors (反馈) — check_ds_alignment, check_min_lines, verify-report-quality
  ④ Guardrails (护栏) — pre_tool_call hook, pre-commit hook
  
Loop = Time dimension:
  L1 (秒级) — 每§生成后自我反思(self_reflect)
  L2 (分钟级) — 跨会话状态管理(状态文件+恢复+熔断)
  L3 (天/周级) — 学习飞轮(失败→规则→测试→回归)
```

## 目录结构

```
skills/bazi/harness-engine/
├── workflow/workflow_v2.yaml    # 流程定义(24§)
├── rules/*.yaml                 # 独立规则文件(24个)
├── templates/*.md               # 输出模板(24个)
├── engine/
│   ├── workflow_v2.py           # 工作流引擎
│   └── step_runner.py           # 步骤执行器(v3含L1+L2)
├── test_suite/
│   ├── regression.py            # 回归测试运行器
│   ├── test_zhu_ren.json        # 测试用例(魏启令)
│   └── test_ziyuan.json         # 测试用例(子源)
└── output/state/                # L2状态文件
```

## 24§规则映射

| § | 规则文件 | 模板文件 | 主要规则 |
|:-:|:---------|:---------|:---------|
| 1 | overview.yaml | overview.md | 八字排盘/空亡/纳音/起运 |
| 2 | geju.yaml | geju.md | 月令藏干/透干/杂气格 |
| 3 | shen_qiang_ruo.yaml | shen_qiang_ruo.md | 身强/中和/身弱判定 |
| 4 | xi_yong_shen.yaml | xi_yong_shen.md | 喜用神判定 |
| 5 | zai_huo_ji_bing.yaml | zai_huo_ji_bing.md | 五行过三断病/七杀断病 |
| 6 | xing_ge.yaml | xing_ge.md | 五重人格 |
| 7 | wai_mao.yaml | wai_mao.md | 五行主外形 |
| 8 | cai_fu.yaml | cai_fu.md | 财星+开财库+食伤生财 |
| 9 | zhi_ye.yaml | zhi_ye.md | 置业方位/大运窗口 |
| 10 | shi_ye.yaml | shi_ye.md | 月干十神+身强弱+日支十神 |
| 11 | xue_ye.yaml | xue_ye.md | 文昌/印星/学业趋势 |
| 12 | hun_yin.yaml | hun_yin.md | 婚姻宫十神/配偶特征 |
| 13 | zi_nv.yaml | zi_nv.md | 时柱十神/子女特征 |
| 14 | jian_kang.yaml | jian_kang.md | 五行脏腑对应/养生 |
| 15 | liu_qin.yaml | liu_qin.md | 四柱六亲分析 |
| 16 | shi_jian.yaml | shi_jian.md | 大运事件总表 |
| 17 | da_yun.yaml | da_yun.md | 每运判运精析 |
| 18 | san_jue_duan.yaml | san_jue_duan.md | 身决/财决/官决 |
| 19 | yun_cheng.yaml | yun_cheng.md | 一生三段运 |
| 20 | wu_xing_bu_chong.yaml | wu_xing_bu_chong.md | 五行补充方案 |
| 21 | ren_sheng_jian_yi.yaml | ren_sheng_jian_yi.md | 综合人生建议 |
| 22 | bu_wen_chang.yaml | bu_wen_chang.md | 补文昌方位 |
| 23 | kai_cai_ku.yaml | kai_cai_ku.md | 开财库方案 |
| 24 | yi_sheng_ding_xing.yaml | yi_sheng_ding_xing.md | 一生定性综评 |

## 关键教训（本session）

### 1. 8字段/八字段索引Bug
❌ 错误：`G = [B8[0], B8[2], B8[4], B8[6]]` → 取成[年干,日干,年支,日支]
✅ 正确：`G = B8[0:4]`（前4=天干）`Z = B8[4:8]`（后4=地支）
✅ 更安全：直接用DS['年干'], DS['月干']等字段名
后果：主母月令取成了"壬"（应为"未"），所有报告天干地支数据对调

### 2. 十神阴阳规则（bazi-data-source.py已修正）
同阴阳=偏印/劫财/七杀/伤官/偏财
异阴阳=正印/比肩/正官/食神/正财
calc_shishen()中偏印/正印和七杀/正官条件反了
后果：子源年支乙木对丙火=正印(旧代码返回偏印)，主母月支藏干全乱

### 3. 中和规则缺失（已补充）
apply_cai_fu_rules和apply_shi_ye_rules的shen_rules匹配链
原只有身强/从弱/身弱三态，缺中和分支
子源报告财富和事业显示[待生成]
已补rules/cai_fu.yaml和rules/shi_ye.yaml + step_runner.py elif链

### 4. 状态文件跨人污染
魏启令跑完后output/state/pipeline.state残留
子源启动时检测到[L2恢复:已完成3个§] → 跳过全部(因为state来自魏启令)
修复：每人独立运行前rm state，或在step_runner中用八字hash校验归属

### 5. 传感器适用边界
check_ds_alignment和check_min_lines针对完整24§报告设计
只跑2-3个§时false positive(八字在§1不在§8/§10)
传感器结果仅在full run时采纳，单§调试时忽略

### 6. pre_tool_call_hook.py是死文件
在hooks目录里存在但未被任何config引用（config.yaml只引用precheck.sh）
已清理确认：实际起作用的只有precheck.sh→precheck.py链路

### 7. 复制模板Bug
生成主母/子源报告时复制了魏启令模板只替换名字
新铁律：每份报告用各自数据源独立生成，独立验证八字不混用
