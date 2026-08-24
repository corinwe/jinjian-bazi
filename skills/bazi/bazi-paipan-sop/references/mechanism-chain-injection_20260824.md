# 机制链注入法（Mechanism Chain Injection）v1.0

> **编制日期**：2026-08-24
> **来源**：老板批评"报告拉垮"（0.9万字 vs 合格基准3.7万字，只有24%）后的根因复盘
> **核心原则**：**"给 Agent 的不是知识库，是【用知识的路径】"**
> **一句话**：把命理推理链用确定性代码生成、直接注入报告头部，LLM 照着链展开论述，而不是让 LLM 自己去技能库里检索规则。

---

## 一、为什么要做：知识在库 ≠ 知识可用

### 事实（2026-08-24 七七/左左报告事故）

- Agent **已经加载了全部命理技能**（foundation/wealth/marriage/children...全在库里）
- 但产出报告只有 8,926/10,246 字（合格基准 37,227/42,408 字）= **24%**
- 每§只有"1张表+几句标签"，旧报告每§有 5-10 个##子结构（分年龄段/分大运/多流派验证）

### 根因

**让 LLM 自己"加载技能→检索规则→拼接推理"这条路不可靠**：
1. LLM 可能跳过技能加载（本次就是：一个技能都没加载）
2. 加载了也可能不引用（知识在 context 里但没被"用"）
3. 拿到的规则是"散点"，LLM 需要自己拼成机制链——拼接质量不稳定

### 结论

```
知识库（技能库/Chroma） = 原料仓库
机制链注入 = 配方单（直接把"怎么用这些原料"写死给LLM）
```

**LLM 不需要检索，照着机制链展开论述 → 产出自然是"分析"而非"标签"。**

---

## 二、机制链的定义

机制链 = **从引擎JSON确定性生成的推理链**，格式：

```
【机制链】<主题>: <数据点1> → <数据点2> → ... → <结论>
```

示例（七七·财星）：
```
【机制链】财星: 分布[月令40.0分、日支12.0分、时支12.0分] → 总分64.0分大富
  → 身弱财旺 → 富屋贫人，需印比运变现 → 最佳变现运: 壬子
```

这条链把"财星64分大富"从标签升级为机制：
- 数据点1：财星分布（月令40/日支12/时支12）→ 说明财从哪来
- 数据点2：总分64 → 大富层次
- 数据点3：身弱财旺 → 富屋贫人（身财匹配）
- 数据点4：需印比运变现 → 何时能拿到钱
- 数据点5：最佳变现运壬子（51-60岁）→ 精确到时间窗

**LLM 拿到这条链，只需要把它展开成3-5段论述**——财星来源、富屋贫人的困境、变现窗口——深度自然到位。

---

## 三、9条标准机制链（确定性生成器已实现）

脚本：`/root/.hermes/profiles/jinjian-zhenren/scripts/mechanism-chain-generator.py`

```
用法:
python3 mechanism-chain-generator.py <engine.json> [--out 输出文件]
例:
python3 mechanism-chain-generator.py /tmp/qiqi_engine.json --out /tmp/qiqi_chain.txt
```

| # | 机制链 | 数据来源（引擎JSON） | 生成逻辑 |
|:-:|:-------|:---------------------|:---------|
| 1 | 身强弱 | `analysis.shen_qiang_ruo` | 计分明细→判定→喜忌方向 |
| 2 | 财星 | `analysis.cai_xing` + 身强弱 | 分布→总分→身财匹配→变现运 |
| 3 | 格局 | `analysis.ge_ju` | 取格→顺逆用→成败标记(合绊/不成格) |
| 4 | 婚姻 | `result.sec_12_marriage` | 配偶星→夫妻宫→质量→窗口 |
| 5 | 学业 | `result.sec_11_education` | 印星+文昌→学历层级 |
| 6 | 子女 | `result.sec_13_children` | 数量→方向→添丁窗口 |
| 7 | 事业 | `result.sec_10_career` | 方向→类型→等级 |
| 8 | 健康 | `result.sec_14_health` + energy | 七杀病灶+偏印淤堵+五行偏旺 |
| 9 | 大运 | `result.sec_1_overview` | 起运→最佳/最差大运 |

**全部确定性逻辑（Python代码），无LLM参与，同一天同一JSON永远输出同一机制链。**

---

## 四、注入格式（报告头部标记·物理门禁依据）

报告头部**必须**包含（pre-commit 强制检查）：

```markdown
<!-- 【机制链注入】 v1.0 2026-08-24 20:08 确定性引擎生成，LLM须照链展开论述，禁止跳过 -->
【机制链】身强弱: ...
【机制链】财星: ...
【机制链】格局: ...
【机制链】婚姻: ...
【机制链】学业: ...
【机制链】子女: ...
【机制链】事业: ...
【机制链】健康: ...
【机制链】大运: ...
```

**LLM 义务**：每一§的分析必须**呼应**对应机制链（可以扩展、可以引用、可以补充规则细节），**禁止跳过机制链直接写标签**。

---

## 五、与现有体系的关系（不是替代，是增强）

```
旧流程（已失效）:
  引擎JSON → [LLM自由发挥] → 报告（可能变标签）

新流程（机制链注入）:
  引擎JSON → mechanism-chain-generator.py → 机制链(确定性)
       ↓
  机制链 + 引擎JSON → [LLM照链展开] → 报告（机制链展开 = 分析）
       ↓
  pre-commit门禁: 检查报告头部是否带【机制链注入】标记
```

### 与 pre_retrieval_hook（Chroma知识注入）的区别

| 维度 | Chroma知识注入（已有） | 机制链注入（新增） |
|:-----|:----------------------|:-------------------|
| 注入内容 | 知识块（规则/原文/案例） | 本命局的推理链（数据→结论） |
| 作用 | 告诉LLM"有哪些规则可用" | 告诉LLM"这条命怎么断" |
| 粒度 | 通用知识（千人一面） | 每人每命唯一 |
| 可靠性 | 需要LLM自己拼接 | 确定性代码拼好 |

**两者配合**：机制链给"推理骨架"，Chroma给"规则血肉"——LLM 用机制链当提纲，用知识块当论据。

---

## 六、物理门禁（pre-commit强制）

见 git hook `weiwuji-knowledge-base/.git/hooks/pre-commit` 新增检查：

```bash
# ④ 机制链注入检查（2026-08-24新增）
if ! grep -q "【机制链注入】" "$FULL_PATH"; then
    echo "  ❌ 缺少【机制链注入】标记！禁止绕过流水线手写报告"
    echo "     运行: python3 /root/.hermes/profiles/jinjian-zhenren/scripts/mechanism-chain-generator.py /tmp/${NAME}_engine.json --out /tmp/${NAME}_chain.txt"
    echo "     然后把机制链粘贴到报告头部"
    HAS_ERROR=1
fi
```

**效果**：绕过引擎流水线手写的报告（没有机制链标记）会被 git commit 直接拒绝。

---

## 七、使用步骤（Agent写报告时必须执行）

```bash
# Step 1: 跑引擎 → 保存engine.json
python3 pipeline_v5.py ...  # 或 run_pipeline
# → 保存到 /tmp/{姓名}_engine.json

# Step 2: 生成机制链
python3 /root/.hermes/profiles/jinjian-zhenren/scripts/mechanism-chain-generator.py \
  /tmp/{姓名}_engine.json --out /tmp/{姓名}_chain.txt

# Step 3: 报告头部粘贴机制链（cat /tmp/{姓名}_chain.txt 内容）

# Step 4: 每个§对照机制链展开论述（不是贴标签）

# Step 5: git commit（pre-commit会校验机制链标记+行数+格式）
```

---

## 八、验收标准

| 检查项 | 标准 |
|:-------|:-----|
| 报告头部带【机制链注入】标记 | ✅ 必须（pre-commit强制） |
| 每§呼应对应机制链 | 人工/Checker检查 |
| 总行数 | ≥800行（旧基准1842行，新报告至少过半） |
| 纯字数 | ≥15000字（旧基准37000字） |
| 每§有子结构 | 分年龄段/分大运/机制链展开，禁止单表+标签 |
| 模糊描述 | 禁用"配偶宫一般，需看大运配合"类空话 |

---

## 九、版本记录

| 版本 | 日期 | 变更 |
|:-----|:-----|:-----|
| v1.0 | 2026-08-24 | 初版：机制链定义+生成器+注入格式+物理门禁 |
| v1.1 | 2026-08-24 | 新增产物溯源(PIPELINE-SIG签名)+强制入口(report-pipeline-entry.py)+强制5法对照 |

---

## 十、强制5法落地清单（2026-08-24 老板校准）

> 老板提供「强制5法」框架（入口收敛/物理门禁/产物溯源/Maker-Checker/Hook注入SOP），
> 逐项对照我们八字体系，确保"规则被执行"不再依赖Agent自觉。

| # | 强制法 | 我们落地 | 状态 |
|:-:|:-------|:---------|:----:|
| 1 | **入口收敛** | `report-pipeline-entry.py` 唯一入口：引擎JSON→机制链→骨架→报告。手写JSON翻译无入口文件→pre-commit拒绝（无机制链标记） | ✅ |
| 2 | **物理门禁** | pre-commit v3.3：quotepath修复+死代码修复+机制链检查+签名校验+质量门禁(≥800行/21§) | ✅ |
| 3 | **产物溯源** | `mechanism-chain-generator.py` 生成PIPELINE-SIG=sha256(八字+身强弱+格局+喜用+财星+最佳大运)，`verify-pipeline-sig.py` 独立校验 | ✅ |
| 4 | **Maker/Checker** | 生成器(确定性代码)=Maker；`verify-pipeline-sig.py`+`verify-report-quality.py`+pre-commit=Checker。人写人审需用maker-checker-workflow技能 | ⚠️ 半自动 |
| 5 | **Hook注入SOP** | pre_llm_call hook(inject-context.sh)注入物理约束提醒 + pre_tool_call hook(precheck.py)拦截未验证写文件 | ✅ |

### 关键文件索引

| 文件 | 作用 |
|:-----|:-----|
| `scripts/mechanism-chain-generator.py` | 机制链+签名生成（确定性） |
| `scripts/verify-pipeline-sig.py` | 签名验证（pre-commit调用） |
| `scripts/report-pipeline-entry.py` | 深度报告强制入口（骨架+机制链） |
| `scripts/verify-report-quality.py` | 质量门禁（≥800行/21§/DS引用） |
| `.git/hooks/pre-commit` (v3.3) | 物理门禁主入口 |
| `config/hooks-backup/pre-commit-knowledge-base-v3.2` | hook备份 |

### 产物溯源原理

```
引擎JSON → mechanism-chain-generator.py
  → sha256(八字+身强弱+格局+喜用+财星+最佳大运) = PIPELINE-SIG
  → 注入报告头部 # PIPELINE-SIG: <hash>

验证: verify-pipeline-sig.py <报告> <引擎JSON>
  → 重算hash vs 报告中hash
  → 一致=确由该引擎JSON生成（可溯源）
  → 不一致=手写/篡改 → pre-commit拒绝
```

### 遗留项（下一轮补齐）

- [ ] Maker/Checker 全自动：生成→独立Checker Agent按质量清单校验→不合格自动打回
- [ ] report-pipeline-entry.py 集成进 bazi-pipeline.sh 主流程
- [ ] 深析报告骨架模板（旧报告1842行提炼）固化到 detailed-skeleton.md
