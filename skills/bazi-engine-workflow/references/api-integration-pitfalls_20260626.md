# API集成与前端数据映射 · 踩坑录

## 背景
bazi-platform 后端通过 subprocess 调用 bazi-engine.py，前端渲染 21§ 结构化 JSON。
本文件记录集成过程中发现的坑位。

## 坑1：paipan.py 自行重写 vs bazi-engine.py 复用

**错误做法**：从零写 paipan.py 做排盘（月柱/日柱全部算错）
**正确做法**：subprocess 调用已验证的 bazi-engine.py

**教训**：任何排盘需求，第一反应是调用 bazi-engine.py，不是从零写！

## 坑2：bazi-engine.py JSON 使用中文键名

```python
data = json.loads(result.stdout)
# ✅ 正确：data["四柱"]["年柱"]   → "庚申"
# ❌ 错误：data["bazi"]["year"]   → KeyError
# ❌ 错误：data["year_pillar"]    → KeyError
```

所有键名都是中文，包括：八字、四柱、纳音、藏干、十神、身强弱、大运、日主
每次解析前先 `print(data.keys())` 确认字段名。

## 坑3：shi_chen 需要自行映射

bazi-engine.py JSON 输出中没有 "shi_chen"（时辰中文名）字段！
```python
shi_chen_names = {0:"子时",2:"丑时",4:"寅时",6:"卯时",8:"辰时",10:"巳时",
                  12:"午时",14:"未时",16:"申时",18:"酉时",20:"戌时",22:"亥时"}
pai["shi_chen"] = shi_chen_names.get(hour, str(hour) + "时")
```
不设置 → 前端显示 "undefined"。

## 坑4：ri_zhu 是对象不是字符串

```json
"日主": {"gan": "辛", "wx": "金"}  // 不是 "辛金"
```

前端渲染时必须处理：
```javascript
if (typeof v === 'object') return (v.gan || '') + '(' + (v.wx || '') + ')';
// 输出: "辛(金)"
```
直接 `${v}` → "[object Object]"。

## 坑5：Section key 必须与API返回一致

前端引用的 section key 必须与 pipeline_v4 输出的 key 完全匹配：

| 前端引用（错误） | API实际返回（正确） |
|:---|:---|
| `r.sec_4_tiao_hou` | `r.sec_4_xi_yong` |
| `r.sec_5_yong_shen` | `r.sec_5_za_i_hui` |
| `r.sec_6_shi_shen` | `r.sec_6_character` |
| `r.sec_13_family` | `r.sec_15_family` |
| `r.sec_14_children` | `r.sec_13_children` |

映射错误 → tab 点开显示 "暂无数据"。

## 坑6：pyc 缓存导致修了等于没修

修改引擎代码后 __pycache__ 中的 .pyc 文件不会自动失效。
必须手动删除缓存+杀旧进程+重启。

```bash
find /root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform -name '__pycache__' -exec rm -rf {} + 2>/dev/null
pkill -f "python main.py"
# 等2秒
cd projects/bazi-platform/backend && python main.py
# 验证：ss -tlnp | grep 8000 确认新进程占用
```

旧进程不杀 → 新进程绑定端口失败 → 用户看到的还是旧结果。

## 坑7：引擎 IMPORT 只能在函数内执行（lazy import）

bazi-engine.py 依赖 ephem 天文库，在模块级别 import 会显著拖慢启动速度。
且 engine 目录通过 sys.path.insert 动态添加，必须在函数内部 import 才能生效。

```python
# ✅ 正确：在函数内部 import
def run_full_analysis_v4(...):
    from lunar import lunar_to_solar, validate_date
    from pipeline_v4 import run_v4
    from constants import BaZi, Pillar

# ❌ 错误：在模块级别 import（启动慢+路径未配置）
from pipeline_v4 import run_v4  # ❌
```
