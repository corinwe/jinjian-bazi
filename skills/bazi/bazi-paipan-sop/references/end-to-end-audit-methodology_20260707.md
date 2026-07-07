# 端到端全量审计方法论 — 2026-07-07实战记录

> **触发**：2026-07-07老板要求端到端审计整个排盘→报告流程。
> **发现**：4个bug（3个skill_view名错误 + 1个引擎字段路径错误 + 2个Python API错误）。
> **结论**：逐文件逐路径审计是发现 SOP/技能/代码 不一致的最有效手段。

## 审计五步法

### Step 1 — 路径物理存在性
```
对HERMES.md/config.yaml/SOP中引用的每个路径：
  test -f <路径> && echo 'EXISTS' || echo 'MISSING'

重点查：
  □ 脚本路径（scripts/xxx.sh/py）
  □ 技能路径（skills/xxx/SKILL.md）
  □ hook路径（hooks/bazi-mandatory/xxx.sh）
  □ 引用的配置文件
```

### Step 2 — skill_view名称 vs frontmatter name一致性
```
对每个 skill_view('xxx')：
  1. 找 xxx 对应的 SKILL.md
  2. 读 frontmatter 的 name: 字段
  3. 对比：skill_view('xxx') 里的 xxx 是否等于 name 字段

🚨 常见错误：skill_view('bazi/bazi-xxx') 但 frontmatter name='bazi-xxx'
```

### Step 3 — Python API调用正确性
```
对SOP/代码中每段Python代码：
  1. 读被调用函数的实际签名（def xxx(...)）
  2. 确认参数名称/类型/顺序匹配
  3. 确认返回值类型（dict vs object）
  4. 确认被调用模块的import路径正确

🚨 常见错误：
  □ paipan()返回dict但调用了.summary()（BaZi方法）
  □ paipan()返回dict直接传run_v5()（需要BaZi对象）
```

### Step 4 — 引擎数据字段路径对齐
```
对SOP中写的提取路径，用实际引擎跑一遍确认：
  result['sec_3_shen_qiang_ruo']['score']  → 是否真有？
  result['大运']['序列']                    → 引擎实际用sec_17_da_yun_detail
  
验证命令：
  python3 -c "from pipeline_v5 import run_v5; ...; 
  for k in sorted(result): print(f'{k}: {type(result[k]).__name__}')"
```

### Step 5 — 规则完整性覆盖
```
对每个核心规则，grep技能文件确认已写入：
  grep -cE '<pattern>' <SKILL.md>
  
规则清单示例：
  □ 大运年龄ceil向上取整
  □ 大运天干地支分开判喜忌
  □ 大运前5年天干70%/后5年70%
  □ 流年上午天干/下午地支
  □ 配偶特征只列实际地支
  □ 人物报告禁止写入/root/
```

## 本会话审计发现（2026-07-07）

| # | 位置 | 错误 | 修复 |
|:-:|:-----|:-----|:-----|
| 1 | bazi-paipan-sop Phase1 | `skill_view('bazi/bazi-foundation-analysis')` → 实际名`bazi-foundation-analysis` | 去掉`bazi/`(共3处) |
| 2 | bazi-paipan-sop Phase3.2 | `data['大运']['序列']` 等字段路径是臆想的 | 改为 `result['sec_17_da_yun_detail']['list']` |
| 3 | bazi-paipan-sop Phase2.2 | `paipan()` 返回dict但调用了`.summary()` (BaZi方法) | 改用 `get_full_paipan()` |
| 4 | bazi-paipan-sop Phase3.1 | `paipan()` 返回dict不能传 `run_v5()` | 改为 `get_full_paipan`→`BaZi`→`run_v5` |
