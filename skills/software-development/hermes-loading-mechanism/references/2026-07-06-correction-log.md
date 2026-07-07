## 2026-07-06 加载机制修正全实录

### 第1轮纠正（老板指出）
我写了BOOTSTRAP.md + preflight.sh手动加载流程
→ 老板问：你每次任务前加载这些文件吗？
→ 我：没加载
→ 老板：纸上流程，没强制力

### 第2轮纠正（老板指出）
我以为是「叠加载」
→ 老板贴源码：prompt_builder.py L1955
→ `or`链，找到第一个就停，项目级只加载1个
→ AGENTS.md只是第2优先级，被.hermes.md挡路就永不被加载

### 第3轮纠正（老板指出）
SOUL.md和AGENTS.md不是二选一，是系统级+项目级两条线
→ SOUL.md = profile根目录·自动加载（系统级）
→ AGENTS.md / HERMES.md = 工作目录·or链（项目级）

### 第4轮纠正（老板指出）
→ 我把bazi铁律放SOUL.md → 不对，SOUL.md只留系统级
→ 我把bazi项目级规则放进**根目录**HERMES.md → 不对，应放`07-国学哲学/八字命格/HERMES.md`
→ 我删了知识库AGENTS.md+恢复了旧版 → 越界了

### 最终现固结构
```
~/.hermes/profiles/jinjian-zhenren/
├── SOUL.md                          ← 系统级（角色/原则/系统铁律）

bazi-platform/
├── HERMES.md                        ← bazi排盘SOP（代码项目）

weiwuji-knowledge-base/
├── HERMES.md                        ← 知识库全局（金久维护）
├── 07-国学哲学/
│   └── 八字命格/
│       └── HERMES.md                ← bazi排盘SOP（知识库·我维护）
```
