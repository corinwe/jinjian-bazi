# Post-Tool-Call Hooks 架构（物理硬化层）

> **来源**：2026-07-16 全面硬化
> **定位**：SOP Phase 7 的自动前置校验，在写文件阶段即拦截格式错误

## 一、Hook 栈

```
write_file / patch 操作
  │
  ├─ [pre_tool_call] bazi-mandatory/check.sh
  │   审计日志记录（耗时+结果） → ~/.hermes/logs/tool_audit/
  │
  └─ [post_tool_call] 自动触发子校验
       ├─ verify-format.py ← §顺序是否符合模板
       │   校验逻辑：九龙道长版→21§顺序匹配STANDARD_SECTIONS
       │             泉师兄版→检查盲派核心概念关键词
       │   日志：~/.hermes/logs/verify/format_warnings.log
       │
       └─ verify-energy.py ← 能量表是否遗漏位置
            检查写文件后是否有常见遗漏位置（年支中气等）
            日志：~/.hermes/logs/verify/warnings.log
```

## 二、Hook 文件位置

```
/root/.hermes/hooks/bazi-mandatory/
├── check.sh              # 主入口（审计日志 + 调度子校验）
├── verify-format.py      # §格式校验
└── verify-energy.py      # 能量表穷举校验
```

## 三、verify-format.py 的校验逻辑

```yaml
九龙道长版报告（21§标准）:
  扫描文件中所有 §N 标题
  对比 STANDARD_SECTIONS 数组（共21项）
  每个§的标题必须包含对应标准标题的前4个字
  警告写入 format_warnings.log（不block写文件，observer-only）

泉师兄盲派版报告:
  扫描文件中是否含盲派核心概念关键词
  缺失关键词 > 3个 → 记录警告
```

## 四、STANDARD_SECTIONS（21§锁定顺序）

```
§1 八字排盘
§2 格局判定
§3 身强弱分析
§4 用神取用与层级论
§5 十神详解与性格分析
§6 财富分析
§7 事业与名望分析
§8 婚姻与家庭分析
§9 子女分析
§10 健康与疾病分析
§11 大运总论
§12 早年大运详解
§13 中年大运详解
§14 当前大运与流年分析
§15 晚年大运详解
§16 大运流年应事总表
§17 空亡·墓库·神煞
§18 五行流通与平衡
§19 六亲关系
§20 化解与建议
§21 总结
```

## 五、已知局限

- hooks 为 observer-only（返回值被系统忽略），无法强制block写操作
- verify-format.py 只在文件路径含「九龙道长版」/「泉师兄」时触发
- 纯 observer 层日志不展示在对话中，需人工查阅日志文件
