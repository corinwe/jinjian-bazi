# 端到端加载链审计方法论

> 2026-07-07 首次执行发现：HERMES.md路径错误、check.sh钩子引用缺失脚本、34个空文件夹、4条散落规则
> 确保能系统化发现所有"靠AI记忆而非物理化"的问题

---

## 审计五步法

### Step 1 — 加载链追查
逐文件确认存在性：

| 环节 | 验证 |
|:-----|:------|
| SOUL.md | `test -f profile根/SOUL.md` |
| HERMES.md | `test -f profile根/HERMES.md` |
| config.yaml auto_load | 每个技能 `test -f skills/路径/SKILL.md` |
| hooks | `test -f ~/.hermes/hooks/*/check.sh` + 验证内部引用 |
| 知识库 | `test -d /root/weiwuji-knowledge-base` |

### Step 2 — 路径引用审计
```
grep 'skills/' HERMES.md  → 路径是 skills/ 还是 projects/.../skills/？
```

### Step 3 — 脚本存在性审计
打开钩子脚本，提取所有子脚本引用 → test -f 逐一验证

### Step 4 — 规则散落审计
每个关键规则必须至少在一个技能/引擎/模板中被搜索到。
如果在USER.md/MEMORY.md中才有 → ⚠️ 散落，需固化。

### Step 5 — /root/ 污染审计
```
find /root -maxdepth 1 -type d -name "[0-9]*"   # 空目录
find /root -maxdepth 1 -name "*八字*"            # 人物报告
```

---

## 修复优先级

| 优先级 | 问题 | 修复 |
|:------|:------|:------|
| 🔴 P0 | 路径不存在 | 更新路径或创建 |
| 🔴 P0 | 钩子引用了不存在的脚本 | 创建或移除 |
| 🟡 P1 | 规则散落 | 写入对应技能 |
| 🟡 P1 | /root/下空目录 | rm -rf |
| 🟢 P2 | 命名/位置不规范 | 移动+更新引用 |

---

## 验收标准

```
□ 加载链全部物理存在
□ auto_load技能路径可访问
□ hooks引用脚本全部存在
□ 路径引用真实
□ 规则在技能/引擎/模板中可搜索到
□ /root/无人报告散落+无空目录
```
