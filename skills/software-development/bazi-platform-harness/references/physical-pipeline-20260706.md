# 物理化八字分析管线（2026-07-06 固化）

## 8步完整流程

| 步骤 | 名称 | 输入 | 工具 | 输出 | 备注 |
|:----|:-----|:-----|:-----|:-----|:-----|
| 1 | 排盘 | 年月日时性别姓名 | paipan.py | paipan dict | ⚠️ 必须跑引擎，禁止手算 |
| 2 | 构建BaZi | step1的pillars | constants.py | BaZi对象 | — |
| 3 | 引擎评分 | BaZi对象+birth日期 | pipeline_v5→36模块 | 22个sec_* dict | 所有数据来源 |
| 4 | 加载理论 | 当前§编号 | skill_view('bazi-{topic}') | 规则清单 | 写§前必须加载 |
| 5 | ⛔匹配数据 | step3数据+step4规则 | 人脑 | 验证结论 | **物理闸门：不列规则不能写** |
| 6 | 写分析 | step5结论 | 人脑+文字 | 分析段落 | 本人亲自写 |
| 7 | 自动校验 | 报告+引擎JSON | verify_report.py | 通过/阻断 | **⛔不通过阻断推库** |
| 8 | 推库 | 报告文件 | git | 推库成功 | — |

## verify_report.py

位置：`/root/bazi-platform/scripts/verify_report.py`
触发：知识库`.git/hooks/pre-commit`自动运行
手工运行：`python3 /root/bazi-platform/scripts/verify_report.py --report {路径} --engine {路径}`

### 7项校验

1. 身强弱分数一致 → 与引擎sec_3_shen_qiang_ruo.score对比
2. 财星分数一致 → 与引擎sec_8_wealth.cai_xing_total对比
3. 五行生克方向 → 检查「金生土」等错误写法
4. 十神名称正确 → 检查戊土=正印(非偏印)等
5. 大运年份正确 → 与引擎大运序列对比
6. 喜忌一致性 → §1表格喜忌与引擎一致
7. 空亡一致性 → 空亡与引擎一致
