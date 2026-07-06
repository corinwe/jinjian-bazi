# 2026-07-05 三模块深度审计实战案例

> 用途：记录本次会话对 wealth_v2 / career_v2 / education 三模块的深度审计过程，
> 供未来类似审计任务参考流程和常见陷阱。

## 审计范围

| 模块 | 代码版本 | 对应skill | 审计完成度 |
|:-----|:---------|:----------|:----------:|
| wealth_v2.py | 已审计修复 | bazi-wealth-analysis | 80% |
| career_v2.py | 已审计+修复 | bazi-career-analysis | 70% |
| education.py | 已审计+修复 | bazi-education-analysis | 95% |
| marriage_v2.py | 深度审计(Sub-Agent) | bazi-marriage-analysis | 95% |
| children_v2.py | 深度审计(Sub-Agent) | bazi-children-analysis | 60%(v2.0 vs skill v3.0) |

## 审计流程（已验证有效）

```bash
# Step 1: 加载对应skill查看原始理论
skill_view('bazi-xxx-analysis')

# Step 2: 读取模块全量代码
read_file('/root/bazi-platform/engine/xxx.py')

# Step 3: 逐条对比 skill 规则 vs 代码实现
# 标注：✅ 已实现 / ⚠️ 部分实现 / ❌ 缺失

# Step 4: 检查版本对齐
# 代码头部版本 vs skill头部版本

# Step 5: 检查引用链（谁调用这个模块 + 传入参数是否完整）
search_files('function_name', path='/root/bazi-platform/engine')

# Step 6: 修复 → 测试 → 推库
python3 engine/tests/test_full_suite.py
```

## 发现的典型问题模式

### 模式1：引用链断裂
```
comprehensive_v2.py 传入 education_result 参数 → 但函数体内从未使用
→ 返回的 dict 也没有 education 字段
```
**教训：** 审计模块时，不仅审模块内部代码，还要审 orchestrator 是否真的消费了输出。

### 模式2：重复计算
```
pipeline_v5.run_v5:
  → 外层调 analyze_education() ✅ 第1次
  → comprehensive_v2.run_comprehensive_engine() 内部又调 analyze_education() ❌ 第2次
修复：comprehensive_v2 去掉内部调用，直接使用 pipeline_v5 传入的 education_result 参数
```
**教训：** 审计时检查 pipeline 链路中每个模块只算一次。确定「唯一计算点」原则。

### 模式3：version gap
```
children_v2.py 标注 v2.0 (2026-06-15)
bazi-children-analysis skill 是 v3.0 (2026-06-27)
→ 差了12天+1个大版本 → §9-§16的6个功能块代码未实现
修复：按skill §顺序逐块实现，每块跑一次测试
```
**教训：** 开审第一件事 — 核对代码版本 vs skill版本。

### 模式4：循环自导入
```python
# career_v2.py line 344:
from career_v2 import GUAN_HE_HUA  # 在自己的函数里导入自己
```
**教训：** grep "from <模块名> import" 检查每个模块的循环自导入。

### 模式5：占位符未实现
```python
# career_v2.py _analyze_diu_guan_signal:
# ... (简化：只标记已有的合化分析结果)
```
**教训：** grep "# \.\.\." / "# 简化" / "# TODO" / "pass" 检查占位符代码。

## 并行审计模式（本次新增）

使用 `delegate_task` 并行审独立模块（如 marriage_v2 + children_v2）：

```python
# 两个模块无依赖关系 → 可并行
delegate_task(goal="审计 marriage_v2.py", role="leaf")
delegate_task(goal="审计 children_v2.py", role="leaf")
# 结果各自返回后，汇总修复
```

**适用条件：**
- ✅ 被审计的模块之间无代码依赖
- ✅ 审计策略相同（同铁律⑥对照标准）
- ❌ 如果模块A的输出是模块B的输入 → 必须串行审计

## 修复推库记录

| Commit | 改动文件 | 内容 |
|:-------|:---------|:-----|
| `d61c3f3` | comprehensive_v2, career_v2 | 6项修复：education调用+丢官信号+开官库+级别精细化+循环导入 |
| `2175df2` | comprehensive_v2 | education去重：去掉内部调用，使用pipeline_v5传入参数 |
