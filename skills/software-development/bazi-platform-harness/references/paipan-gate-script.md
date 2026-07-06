# 排盘强制门禁脚本

**路径**: `/root/bazi-platform/scripts/bazi-must-run-engine.sh`
**创建时间**: 2026-06-29
**触发教训**: 梦的日柱手算错误（壬戌→癸亥）

## 用途
任何八字分析前必须先运行此脚本，禁止手算排盘。

## 命令格式
```bash
bash /root/bazi-platform/scripts/bazi-must-run-engine.sh -n <姓名> -g <性别> -y <年> -m <月> -d <日> -h <时>
```

## 输出
- 引擎排盘结果（JSON格式，含八字/十神/大运）
- 带 `_gate_verified` 标记证明已通过门禁
- 所有后续分析必须基于此输出

## 无时辰时
如果不知道时辰，不加 -h 参数：
```bash
bash /root/bazi-platform/scripts/bazi-must-run-engine.sh -n 梦 -g 女 -y 2007 -m 7 -d 27
```
输出12个时辰的排盘结果。

## 物理层依赖
| 文件 | 作用 |
|:-----|:------|
| `/root/bazi-platform/AGENTS.md` | 铁律①自动加载 |
| `/root/bazi-platform/.hermes/config/credentials.md` | 铁律完整版 |
| `bazi-platform-harness/references/project-config.md` | 铁律引用版 |
| `bazi-engine-workflow/SKILL.md` | 日柱计算陷阱固化 |
