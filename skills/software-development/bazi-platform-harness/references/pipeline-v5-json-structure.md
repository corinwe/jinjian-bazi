# pipeline_v5 JSON 输出结构（2026-07-08校准）

## 核心坑点

`pipeline_v5.run_v5()` 输出的 JSON 是**扁平结构**，不是嵌套在 `result` 下的。

### ✅ 正确的访问方式

```python
engine["sec_3_shen_qiang_ruo"]["score"]   # ✅ 扁平访问
engine["sec_8_wealth"]["cai_xing_total"]   # ✅ 扁平访问
engine["sec_1_overview"]["ri_zhu"]         # ✅ 注意 ri_zhu 是 dict
```

### ❌ 错误的访问方式（会返回空）

```python
engine["result"]["sec_3_shen_qiang_ruo"]   # ❌ 没有 result 层
```

### ri_zhu 字段的特殊结构

`sec_1_overview["ri_zhu"]` 是一个 **dict**，**不是字符串**：

```python
ri_zhu = engine["sec_1_overview"]["ri_zhu"]
# ri_zhu = {"gan": "庚", "wx": "金"}

# ✅ 正确提取日干
ri_gan = ri_zhu["gan"]  # "庚"

# ❌ 错误提取：ri_zhu[0] 会报 KeyError
```

## 引擎顶层所有 key

```
meta, sec_1_overview ~ sec_21_advice（共22个顶层key）
```

没有 `paipan`、`bazi`、`basic` 等字段（这些在 `bazi-must-run-engine.sh` 的输出现成中，不在 pipeline_v5 输出的 JSON 里）。

## 验证脚本

```python
import json
engine = json.load(open("/tmp/xxx_engine.json"))
print("顶层keys:", list(engine.keys()))
ri_zhu = engine.get("sec_1_overview", {}).get("ri_zhu", "")
if isinstance(ri_zhu, dict):
    print(f"日主: {ri_zhu['gan']}")
elif isinstance(ri_zhu, str):
    print(f"日主: {ri_zhu}")
```
