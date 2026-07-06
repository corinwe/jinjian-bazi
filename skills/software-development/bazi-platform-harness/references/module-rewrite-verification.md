# 模块大规模重写——零回归验证协议

> 来源：2026-07-05 `misfortune_analysis.py` 审计修复实战（47条规则 15%→100%）
> 适用：任何完整的模块重写（非小修小补）

## 核心原则

**「修完没坏」和「真的没坏」是两回事**——必须用完整的测试基线对比来证明零回归。

## 协议流程

### Step 1: 基线建立（改前）

```yaml
修改前执行一次完整测试：
  cd /root/bazi-platform/engine/tests && python3 test_full_suite.py
  
记录基线指标：
  └─ 总用例数: 361
  └─ PASS: 347
  └─ FAIL: 14
  └─ 通过率: 96.1%
  
记录所有FAIL的用例名和原因（区分预存失败和本次引入的新失败）：
  └─ 预存失败：大运8步→11步、文昌原局不存在、§8.summary字段
  └─ 本次新失败：（改前是0，改后必须也是0）
```

### Step 2: 重写/修复（改中）

执行完整代码修改。完成后必须确认：
- [ ] 模块可导入（`python3 -c "from x import ..."` 无报错）
- [ ] 旧接口向后兼容（原函数签名带默认参数）
- [ ] 新字段存在（`assert 'new_field' in result`）
- [ ] 极端值处理（空列表、None、长度为0）

### Step 3: 回归验证（改后）

```yaml
修改后执行完整测试：
  cd /root/bazi-platform/engine/tests && python3 test_full_suite.py
  
对比基线：
  └─ 总用例数 = 基线总用例数 ✅
  └─ PASS = 基线PASS ✅
  └─ FAIL = 基线FAIL ✅（数量+具体用例名完全一致）
  └─ 通过率 >= 基线通过率 ✅

新增依赖测试：
  └─ pipeline端到端（run_v5 包含新模块则通过）
  └─ JSON序列化（新字段可json.dumps）
  └─ 单独对每个新增字段做断言
```

### Step 4: 管道端到端验证

```yaml
加载上游pipeline并确认：
  └─ pipeline_v5.run_v5() 能正常返回
  └─ 对应§节（如 sec_5_zai_huo）结构完整
  └─ 调用链无断裂（旧到新字段过渡）
```

## 常见陷阱

### 陷阱1：预存失败掩盖新失败

```python
# ❌ 错误：只看通过率
通过率96.1% → 没问题 ✅  # 错！14个FAIL到底是预存的还是新引入的？

# ✅ 正确：逐条对比FAIL列表
old_fails = {"大运步数": 10, "文昌": 2, "§8.summary": 2}  # 改前记录
new_fails = {"大运步数": 10, "文昌": 2, "§8.summary": 2}  # 改后一致 → 零新增
```

### 陷阱2：跳过pipeline端到端

只测模块本身的 `analyze_misfortune()` 函数是不够的——pipeline的 `run_v5()` 传参方式、数据结构打包方式可能与你重写的格式不一致。必须实测 `run_v5()`。

### 陷阱3：只测全量不测新字段

```
# ❌ 错误：全量测试过了，新字段应该也对
# ✅ 正确：单独断言每个新增字段
assert 'qi_sha_bing_fa' in result
assert 'pian_yin_bing_fa' in result
assert 'xue_ren' in result
...
```

## 检查清单

| 检查项 | 命令/验证方式 | □ |
|:-------|:-------------|:--:|
| 改前基线记录 | `python3 test_full_suite.py` 记录PASS/FAIL | □ |
| 模块导入 | `python3 -c "from x import y"` | □ |
| 旧接口兼容 | 最小参数调用无异常 | □ |
| 新字段存在 | `assert '新字段' in result` | □ |
| 改后回归 | PASS/FAIL数量与改前完全一致 | □ |
| pipeline端到端 | `run_v5()` 返回正常含新字段 | □ |
| JSON序列化 | `json.dumps(result)` 无异常 | □ |
