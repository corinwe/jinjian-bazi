# compute_da_yun 参数传递陷阱·2026-07-05

> **现象：** `compute_da_yun()` 函数签名变更后（新增 `birth_month`/`birth_day` 参数），所有使用**位置参数**传 `qi_yun_days` 的调用方全部静默失效：`1.1` 被解释为 `birth_month`，导致 `date(birth_year, 1.1, birth_day)` 报 `TypeError: 'float' object cannot be interpreted as an integer`。

## 根因

**函数签名变更（2026-07-05 大运引擎修复）：**

```python
# ❌ 旧签名（3个位置参数）
def compute_da_yun(bazi, birth_year=1980, qi_yun_days=None):

# ✅ 新签名（5个位置参数，新增 birth_month/birth_day）
def compute_da_yun(bazi, birth_year=1980, birth_month=1, birth_day=1, qi_yun_days=None):
```

**所有旧调用方用了位置参数：**
```python
# ❌ 错误（位置参数传qi_yun_days）
compute_da_yun(p, person["birth_year"], 1.1)
# → 1.1 被解释为 birth_month!

# ✅ 正确（关键字参数）
compute_da_yun(p, person["birth_year"], qi_yun_days=1.1)
```

## 影响范围

所有调用了 `compute_da_yun()` 并传了 `qi_yun_days` 位置参数的代码：

| 文件 | 行号 | 修复情况 |
|:-----|:----:|:---------|
| `tests/test_full_suite.py` | 274, 280, 435, 478 | ✅ 4处改为关键字参数 |
| `engine/pipeline_v5.py` | 614 | ✅ run_pipeline 补了birth_day参数 |

## 教训

```yaml
【函数设计铁律】
  任何有多个可选参数的函数：
  ✅ 为经常被跳过的参数使用关键字参数传参
  ✅ 调用方：用 `param=value` 格式，不用位置参数
  ✅ 函数签名：保持 backward compat（新增参数加到末尾，不插中间）
  
  具体到 compute_da_yun：
  - birth_month, birth_day 虽然是"中间的"参数，但测试中经常只传qi_yun_days
  - 如果测试不想传birth_month/birth_day，用关键字：
    compute_da_yun(bazi, birth_year=1980, qi_yun_days=1.1)

【自检清单】（修改函数签名后）：
  □ 搜索所有调用方：grep -rn "compute_da_yun" 项目目录
  □ 逐一检查位置参数顺序是否正确
  □ 运行完整测试：python3 tests/test_full_suite.py
  □ 特别检查第3/4个位置参数是否被新参数"吃掉"
```

## 搜索命令

```bash
# 查找所有 compute_da_yun 调用 + 查看传参方式
grep -rn "compute_da_yun" projects/bazi-platform/engine/ --include="*.py"

# 运行测试
cd projects/bazi-platform/engine/tests && python3 test_full_suite.py
```

## 关联参考

- `bazi-engine-workflow` `references/大运引擎int截断Bug与节气计算修复_20260705.md` — 同一轮修复中的大运引擎改动
- `references/已知陷阱_引擎门禁_20260704.md` — 引擎门禁通用陷阱集合
