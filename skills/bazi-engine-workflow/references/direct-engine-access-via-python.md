# 直接Python导入引擎排盘（替代shell脚本）

## 适用场景

当需要快速获取排盘数据而不经过shell脚本/CI管道时，可直接通过Python导入引擎模块。

## 引擎API

```python
import sys
sys.path.insert(0, 'projects/bazi-platform/engine')
from paipan import paipan

result = paipan('姓名', '男/女', 出生年, 出生月, 出生日, 出生时辰)
```

## 返回值结构

`paipan()` 返回有限的字段：
- `name`, `gender`, `birth_date`, `birth_hour`, `shi_chen`
- `bazi`: 八字字符串（如 "丁亥 丁未 壬戌 癸卯"）
- `year_pillar`, `month_pillar`, `day_pillar`, `hour_pillar`: 各柱干支
- 不包含：大运、藏干、身强弱、财星等深度分析

## 局限性

`paipan()` 仅做基础排盘（四柱+时辰）。完整分析（大运/身强弱/财星/格局等30+维度）需：
1. 通过 `pipeline_v5.run_v5()` 获取全量数据
2. 或手动按金鉴真人原始规则逐项计算

## 与 shell 脚本的关系

**铁律①** 要求使用 `bash projects/bazi-platform/scripts/bazi-must-run-engine.sh` 做排盘验证。
- shell 脚本 = 完整验证流水线（含门禁检查）
- Python 导入 = 快速获取原始数据（前置步骤，仍需用脚本做最终验证）

正确流程：
```
Python导入 paipan() → 获取原始八字数据 → 写报告 → shell脚本验证
```

## 异常处理

当 `paipan()` 因依赖问题失败时：
1. 检查 sys.path：须包含 `projects/bazi-platform/engine`
2. 检查 paipan.py 中的函数名：是 `paipan()` 不是 `get_full_paipan()` 或 `paipan_v2()`
3. 检查出生日期范围：paipan() 基于基准日法（2000-01-01=戊午54序），对1950-2050年的日期已验证有效
4. 如排盘失败 → 回退到 shell 脚本 `bazi-must-run-engine.sh`
