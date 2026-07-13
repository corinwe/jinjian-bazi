# 引擎安全过滤：规则标记剥离 + condition字段删除
## 2026-07-09 老板校准

## 背景
报告的「深度命理分析」区泄漏了 `【金鉴真人·xxx规则·】` 内部标记和 `condition` 字段的底层计算逻辑。
老板指出：「很多节，你把符号规则透露出来，这个不能透露，要全部修掉」。

## 修改内容

### 1. `_strip_rule_markers()` 后处理（pipeline_v5.py）
在 `run_pipeline()` 中、`attach_detail_analysis()` 和 `add_narratives()` 之后执行：

```python
import re
def _strip_rule_markers(obj):
    if isinstance(obj, str):
        return re.sub(r'【金鉴真人[^】]*】', '', obj).strip()
    elif isinstance(obj, dict):
        return {k: _strip_rule_markers(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_strip_rule_markers(i) for i in obj]
    return obj
result = _strip_rule_markers(result)
```

位置：pipeline_v5.py run_pipeline() 函数内，在 add_narratives(result) 之后。

### 2. 删除 `sec_2_ge_ju.condition` 字段
原代码：
```python
"condition": f"月令{detail_ge}成立：月令本气定格局{'，天干透出' + str(all_gans[1]) + '确认' if all_gans[1] in xi else '，以月令为基准'}"
```
已删除。该字段纯为调试用途，对用户端无价值且泄漏规则逻辑。

## 安全原则
1. detail_analysis 字段包含规则引擎的确定性分析文本，供 generate_deep_report.py / PDF 等消费
2. 但 `【金鉴真人·】` 标记是内部标签，任何用户端输出前必须剥离
3. 前端侧也需配合：不 fallback 读取 detail / description / analysis 等未知字段

## 验证方法
```bash
# 运行引擎，检查输出中是否包含标记
python3 pipeline_v5.py --name 测试 --gender 男 --year 1980 --month 8 --day 6 --hour 22 --json | python3 -c "
import json,sys; d=json.load(sys.stdin)
print('标记数:', json.dumps(d).count('金鉴真人'))
print('condition存在:', 'condition' in d.get('result',{}).get('sec_2_ge_ju',{}))
"
# 期望输出: 标记数: 1（meta字段的引擎名是合法的）, condition存在: False
```
