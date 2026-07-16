# 数据源物理约束机制

## 为什么需要物理约束？

**问题**：以前数据源在 /tmp/xxx_ds.json 里，但写报告时可以完全不读它，凭记忆写数字。引擎跑了但报告里的数字是编的。

**解决**：4层物理约束，每一层都在不同阶段阻止「凭记忆取数」。

## 约束链

```
约束① — 脚本入口
  report-generator.py 必须收到 DS 参数
  DS 参数只能从 json.load(open(path)) 获得
  没有文件 → 拒绝执行

约束② — 环境变量
  BAZI_DATASOURCE 必须设置
  pre_tool_call_hook 验证存在性
  HOOK.yaml注册 → 每次写文件前自动检查

约束③ — 函数签名
  def module_xxx(DS):  ← 所有模块函数只有DS这一个输入
  DS['藏干十神']  → 读取的是文件数据，不是LLM记忆
  DS['身强弱']['总分']  → 引擎算的分数，不是LLM猜的

约束④ — 报告校验
  Phase 5.1: 数字对齐检查
  身强弱分 / 身强弱等级 / 大运年龄 / 日主 / 藏干
  任一不对齐 → 阻止推库
```

## 触发时序

```mermaid
graph LR
    A[引擎排盘] --> B[engine.json]
    B --> C[bazi-data-source.py]
    C --> D[datasource.json]
    D --> E[export BAZI_DATASOURCE]
    E --> F[pre_tool_call_hook检查]
    F -->|通过| G[report-generator.py<br>def module(DS):]
    F -->|不通过| H[❌ 阻止写报告]
    G --> I[Phase 5.1校验]
    I -->|通过| J[✅ 推库]
    I -->|不通过| K[❌ 修正报告]
```
