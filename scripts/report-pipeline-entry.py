#!/usr/bin/env python3
"""
report-pipeline-entry.py — 深度报告强制入口 v1.0
=================================================
强制5法之「入口收敛」：写八字深度报告的唯一合法入口。

流程（一条命令完成）:
  1. 读取引擎JSON
  2. 生成机制链（含PIPELINE-SIG溯源签名）
  3. 生成报告骨架（21§标题+每§子结构提示）
  4. 校验引擎JSON必须存在（否则拒绝）
  5. 输出报告模板 → Agent按机制链展开填充

用法:
  python3 report-pipeline-entry.py <引擎JSON> --name <姓名> --out <报告路径>
  例:
  python3 report-pipeline-entry.py /tmp/qiqi_engine.json --name 七七 --out /tmp/qiqi_report.md

退出码:
  0 = 成功生成入口模板（Agent继续填充）
  1 = 引擎JSON缺失/无效（禁止写报告）
"""
import sys, os, json, datetime, argparse, subprocess

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
CHAIN_GEN = os.path.join(SCRIPTS_DIR, 'mechanism-chain-generator.py')


def build_skeleton(d: dict) -> str:
    """生成21§报告骨架（每§含子结构提示，防止偷懒）"""
    bazi = d.get('paipan', {}).get('bazi', '') or d.get('result', {}).get('sec_1_overview', {}).get('bazi', '')
    sq = d.get('analysis', {}).get('shen_qiang_ruo', {})
    label = sq.get('label', '')
    score = sq.get('score', '')
    gj = d.get('analysis', {}).get('ge_ju', {})
    main = gj.get('main', '')
    xys = d.get('analysis', {}).get('xi_yong_shen', {})
    xi = '/'.join(xys.get('xi', []))
    ji = '/'.join(xys.get('ji', []))
    cx = d.get('analysis', {}).get('cai_xing', {})
    cai = cx.get('total', 0)
    cai_level = cx.get('wealth_level', '')
    s1 = d.get('result', {}).get('sec_1_overview', {})
    best = s1.get('best_da_yun', '')
    worst = s1.get('worst_da_yun', '')
    qy = s1.get('qi_yun_age', '')

    # 21§骨架（每§强制子结构）
    skeleton = f"""# {{姓名}} · 八字深析报告（21§ 标准版）

> 分析师：金鉴真人体系 | 排盘工具：bazi-engine v5.0（确定性规则引擎）| 报告编号：BZ-{bazi[:2]}-{bazi[2:4]}-03
> 报告日期：{datetime.datetime.now().strftime('%Y-%m-%d')} | 排盘引擎数据：{bazi}

<!-- 此处粘贴机制链（含PIPELINE-SIG） -->

---

## 命盘基本信息

| 项目 | 内容 |
| --- | --- |
| 姓名 | {{姓名}} |
| 出生时间 | {s1.get('birth_info', '')} |
| 八字四柱 | {bazi} |
| 日主 | {s1.get('ri_zhu', {}).get('gan', '') if isinstance(s1.get('ri_zhu'), dict) else s1.get('ri_zhu', '')} |
| 身强弱 | {label}（{score}分） |
| 格局 | {main} |
| 喜用神 | {xi} |
| 忌神 | {ji} |
| 财星 | {cai}分（{cai_level}） |
| 最佳大运 | {best} / 最差大运：{worst} |

---

# §1 一页总览（三大核心分析）
## 1.1 命盘速览表（表格：格局/身强弱/喜用/忌神/财星/事业/婚姻/子女/最佳大运）
## 1.2 【关键调和与关键做工路径】（3句话：用神如何作用、五行如何流通做功）
## 1.3 【强项与弱项】（最强2-3方面 + 最弱2-3风险点）
## 1.4 【关键链路不能断】（最关键能量链，断裂后果）

# §2 格局
## 2.1 格局判定（引擎数据：{main}）
## 2.2 十神分布表（年/月/日/时柱）
## 2.3 格局解读（顺逆用/合绊/成格条件验证·引用规则）
## 2.4 格局层次评估（中上/中下/上等）

# §3 身强弱
## 3.1 引擎评分明细（计分表：月令印/比劫/天干比劫/日支印比/年时支印比）
## 3.2 判定逻辑（为什么这个分数）
## 3.3 身弱/中和实战含义（对人生策略影响）

# §4 喜用神
## 4.1 引擎判定（喜{xi} 忌{ji} 调候）
## 4.2 判定逻辑（引用规则：身弱→喜生扶/身强→喜克泄耗）
## 4.3 行为化解指导（人生实践：做什么事=补用神，不是只给颜色方位）
## 4.4 五行喜忌总表（五行/吉凶/宜忌）

# §5 灾祸疾病
## 5.1 神煞与冲害（自刑/元辰/灾煞/天罗地网表）
## 5.2 五行过三排查（各五行能量表）
## 5.3 灾祸提示（引擎关键事件年份）
## 5.4 分年龄段重点（幼年/青年/中年/晚年）
## 5.5 化解细则（身体/是非/破财/平安）

# §6 性格
## 6.1 日主本性（五行+阴阳）
## 6.2 十神性格分层（每个透干十神独立分析）
## 6.3 性格优势清单
## 6.4 性格改进方向

# §7 外貌
## 7.1 五行身形总论
## 7.2 面相特征（日主+食伤/印星特征）
## 7.3 气质定位
## 7.4 一生外形走势

# §8 财富
## 8.1 财星评分（{cai}分·{cai_level}·明细表）
## 8.2 财星来源解析（月令/日支/时支各代表什么）
## 8.3 破财风险动态判定（按喜忌：身弱防财攻身/身强防比劫夺财）
## 8.4 财富关键时间窗（变现大运：{best}）
## 8.5 理财建议（守财法/攻财法）
## 8.6 财富流年应期表

# §9 置业
## 9.1 置业基因（财库/印星）
## 9.2 置业时机（与身强弱同步）
## 9.3 方位与户型建议
## 9.4 风险提示

# §10 事业
## 10.1 事业格局总判
## 10.2 适合行业方向（按十神归位）
## 10.3 事业关键节点（升迁/变动年份）
## 10.4 事业风险与规避
## 10.5 事业贵人

# §11 学历
## 11.1 学历基因（印星/文昌）
## 11.2 学业阶段详析（幼年/小学初中/高中大学/深造）
## 11.3 学业贵人
## 11.4 学历与事业联动

# §12 婚姻
## 12.1 婚姻格局总判
## 12.2 配偶画像（命理推论：外形/性格/职业）
## 12.3 感情时间线（情窦初开/青年/正缘/中年/晚年）
## 12.4 婚姻风险与化解
## 12.5 合婚宜忌表（生肖/五行/经营要点）

# §13 子女
## 13.1 子女格局总判
## 13.2 子女数量与性别倾向
## 13.3 子女时间线（添丁窗口）
## 13.4 子女成长重点
## 13.5 子女与命主互动

# §14 健康
## 14.1 健康总纲（五行病理）
## 14.2 各年龄段健康重点（0-10/11-20/21-30/31-50/51-70/71+）
## 14.3 一生健康高危流年
## 14.4 养生方案（五行对症）
## 14.5 健康总评

# §15 六亲
## 15.1 六亲总纲（年/月/日/时柱宫位）
## 15.2 父母缘详析（父亲/母亲独立分析）
## 15.3 手足缘
## 15.4 祖辈与家族
## 15.5 六亲应期提示

# §16 流年重点事件总表
## 16.1 童限（0-10岁）
## 16.2 第1步大运（11-20岁）事件
## 16.3 第2步大运（21-30岁）事件
## 16.4 第3步大运（31-40岁）事件
## 16.5 第4步大运（41-50岁）事件
## 16.6 第5步大运（51-60岁）事件
## 16.7 第6步大运（61-70岁）事件
## 16.8 第7-8步大运（71-90岁）事件
## 16.9 一生重大转折点速览（表格：流年|事件类型|事件描述|吉凶）

# §17 大运精析
## 17.1 第1步大运（干支解析/十神流转/各层面应事/流年提示/评级）
## 17.2 第2步大运
## 17.3 第3步大运
## 17.4 第4步大运
## 17.5 第5步大运
## 17.6 第6步大运
## 17.7 第7步大运
## 17.8 第8步大运
## 17.9 大运总览表（大运|起止年龄|起止年份|干支五行|对格局影响|定性描述）

# §18 三决断
## 18.1 财富决断（其人/其事/其时/其度/依据）
## 18.2 事业决断
## 18.3 婚姻决断

# §19 总评
## 19.1 人生曲线（各步大运评分表）
## 19.2 综合评价（早/中/晚三段运各有判断）

# §20 补益
## 20.1 五行补益（颜色/方位/数字/饰品/饮食表）
## 20.2 行为补益（优先：做什么事=补用神）
## 20.3 补财库方案（如适用·具体方位+物品+数字）
## 20.4 补文昌方案（如适用·塔方位+颜色）

# §21 建议
## 21.1 给家长（当前阶段行动清单）
## 21.2 给本人（成年后）
## 21.3 呼应三大核心分析（守能量链/发挥强项防弱项/警惕年份）
## 21.4 一生关键词

---

## 附：排盘验证信息
- 出生时间：{s1.get('birth_info', '')}
- 引擎：bazi-engine v5.0（pipeline_v5 run_pipeline 确定性计算）
- 身强弱/格局/喜用/财星/大运/流年/婚姻/子女/健康 = 引擎JSON直接提取，LLM仅做翻译
- 机制链注入：✅（含PIPELINE-SIG溯源签名）

*基于传统子平命理框架，仅供文化娱乐参考。*
"""
    return skeleton


def main():
    parser = argparse.ArgumentParser(description='深度报告强制入口')
    parser.add_argument('engine_json', help='引擎JSON路径')
    parser.add_argument('--name', required=True, help='姓名')
    parser.add_argument('--out', required=True, help='输出报告路径')
    args = parser.parse_args()

    # 1. 引擎JSON必须存在且有效（入口收敛核心）
    if not os.path.exists(args.engine_json):
        print(f"❌ 引擎JSON不存在: {args.engine_json}")
        print("   请先运行引擎生成JSON，禁止直接手写报告")
        sys.exit(1)
    try:
        with open(args.engine_json, encoding='utf-8') as f:
            d = json.load(f)
    except Exception as e:
        print(f"❌ 引擎JSON无效: {e}")
        sys.exit(1)

    # 2. 生成机制链（含PIPELINE-SIG）
    chain_out = os.path.join('/tmp', f'{args.name}_chain.txt')
    r = subprocess.run(
        [sys.executable, CHAIN_GEN, args.engine_json, '--out', chain_out],
        capture_output=True, text=True, timeout=30
    )
    if r.returncode != 0:
        print(f"❌ 机制链生成失败: {r.stderr[:200]}")
        sys.exit(1)
    with open(chain_out, encoding='utf-8') as f:
        chain = f.read()

    # 3. 生成骨架
    skeleton = build_skeleton(d)
    skeleton = skeleton.replace('{姓名}', args.name)
    # 4. 注入机制链到头部（替换占位符）
    skeleton = skeleton.replace('<!-- 此处粘贴机制链（含PIPELINE-SIG） -->', chain.strip())

    # 5. 写出
    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(skeleton)
    print(f"✅ 报告入口模板已生成: {args.out}")
    print(f"   机制链+PIPELINE-SIG已注入头部")
    print(f"   下一步: Agent按骨架展开填充（每§≥500字，对照机制链论述）")
    sys.exit(0)


if __name__ == '__main__':
    main()
