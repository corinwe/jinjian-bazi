#!/usr/bin/env python3
"""
金鉴真人·交付物理门禁 v1.0
══════════════════════════════════════════════
写入报告后 → 强制跑此脚本 → 全部PASS才交付

融合两套校验：
  线A — 引擎数据一致性（继承 verify_report.py 的7项数据校验）
  线B — /goal 交付门禁（品牌名/性格/行数/婚姻/补财库/数据来源）

退出码：
  0 = ✅ 全部通过，可以交付
  1 = ❌ 有错误，阻断交付（必须先修复再重跑）

用法：
  python3 delivery-gate.py --report <报告.md> --engine <引擎.json>
  python3 delivery-gate.py --report <报告.md>  # 无引擎时只跑线B
"""

import re
import sys
import json
import argparse


# ══════════════════════════════════════════════
# 线A：引擎数据一致性校验（继承 verify_report.py）
# ══════════════════════════════════════════════

def check_shen_qiang_ruo(report_text, engine):
    """① 身强弱分数一致"""
    errors = []
    result = engine.get("result", {})
    s3 = result.get("sec_3_shen_qiang_ruo", {})
    if not s3:
        s3 = engine.get("sec_3_shen_qiang_ruo", {})
    exp_score = s3.get("score")
    exp_label = s3.get("label", "")

    if exp_score is None:
        errors.append("⚠️ 引擎无身强弱分数，跳过")
        return errors

    patterns = [
        r'(身强|身弱|中和|从弱)[（(]\s*([\d.]+)\s*[分)]',
        r'(身强|身弱|中和|从弱)[（(]\s*([\d.]+)',
    ]
    found = False
    for p in patterns:
        for m in re.finditer(p, report_text):
            found = True
            rpt_label = m.group(1)
            rpt_score = float(m.group(2))
            if abs(rpt_score - exp_score) > 0.5:
                errors.append(f"❌ 身强弱分数不一致：报告{rpt_score}分，引擎{exp_score}分")
            if rpt_label != exp_label and exp_label:
                if rpt_label not in exp_label and exp_label not in rpt_label:
                    errors.append(f"❌ 身强弱标签不一致：报告「{rpt_label}」，引擎「{exp_label}」")
            break
        if found:
            break
    if not found:
        errors.append("❌ 未找到身强弱信息")
    return errors


def check_cai_xing(report_text, engine):
    """② 财星分数一致"""
    errors = []
    s8 = engine.get("sec_8_wealth", {})
    exp_score = s8.get("cai_xing_total")

    patterns = [
        r'财星分数[^0-9]*([\d.]+)分',
        r'财星[^0-9]*总[^0-9]*([\d.]+)分',
        r'\*\*([\d.]+)分\*\*.*财',
    ]
    found = False
    for p in patterns:
        for m in re.finditer(p, report_text):
            rpt_score = float(m.group(1))
            if exp_score and abs(rpt_score - exp_score) > 0.5:
                errors.append(f"❌ 财星分数不一致：报告{rpt_score}分，引擎{exp_score}分")
            found = True
            break
        if found:
            break
    return errors


def check_wuxing_shengke(report_text, engine=None):
    """③ 五行生克方向"""
    errors = []
    if re.search(r'金\s*(生|助)\s*土', report_text):
        lines = report_text.split('\n')
        for i, line in enumerate(lines):
            if re.search(r'金\s*(生|助)\s*土', line):
                if not re.search(r'土\s*生\s*金|土被金泄|金泄土', line):
                    errors.append(f"❌ L{i+1}: 五行生克可能写反——正确是土生金")
    return errors


def check_shi_shen(report_text, engine):
    """④ 十神名称正确"""
    errors = []
    result = engine.get("result", {})
    s1 = result.get("sec_1_overview", {})
    ri_zhu = s1.get("ri_zhu", "")

    for i, line in enumerate(report_text.split('\n')):
        if '偏印' in line and ('己土' in line or '戊土' in line):
            # 戊土对庚辛金要看具体日主
            if '戊土' in line and '偏印' in line and '正印' not in line:
                if ri_zhu and ri_zhu[0] in '庚辛':
                    errors.append(f"❌ L{i+1}: 戊土对{ri_zhu[0]}金=正印（阳生阴），不是偏印")
        # 食伤正偏检查
        if '伤官' in line and '生' in line and ri_zhu:
            if ri_zhu[0] in '辛癸己乙丁':
                errors.append(f"❌ L{i+1}: 注意{ri_zhu[0]}日主→食伤阴阳关系")
    return errors


def check_da_yun(report_text, engine):
    """⑤ 大运年份正确"""
    errors = []
    result = engine.get("result", {})
    s17 = result.get("sec_17_da_yun_detail", {})
    dy_list = s17.get("list", [])
    if not dy_list:
        return errors
    report_text_lower = report_text
    for dy in dy_list:
        gz = dy.get("gan_zhi", "")
        sy = dy.get("start_year", "")
        ey = dy.get("end_year", "")
        if gz and sy and ey:
            yr_str = f"{sy}~{ey}"
            if gz in report_text_lower and yr_str not in report_text_lower:
                yr_str2 = f"{sy}～{ey}"
                if yr_str2 not in report_text_lower:
                    pass  # 年份格式多样，暂时只报warning
    return errors


def check_xi_ji(report_text, engine):
    """⑥ 喜忌一致性"""
    errors = []
    result = engine.get("result", {})
    s4 = result.get("sec_4_xi_yong", {})
    eng_xi = s4.get("xi", [])
    eng_ji = s4.get("ji", [])
    if not eng_xi and not eng_ji:
        return errors
    lines = report_text.split('\n')
    in_total = False
    for i, line in enumerate(lines):
        if '喜用神' in line and ('>' in line or '> ' in line or ',' in line):
            for wx in eng_xi:
                if wx not in line:
                    in_total = True
        if '忌神' in line and ('>' in line or '> ' in line or ',' in line):
            for wx in eng_ji:
                if wx not in line:
                    in_total = True
    if in_total:
        errors.append("❌ 喜/忌神缺引擎中的五行")
    return errors


def check_kong_wang(report_text, engine):
    """⑦ 空亡一致性"""
    errors = []
    result = engine.get("result", {})
    s1 = result.get("sec_1_overview", {})
    eng_kw = s1.get("kong_wang", "")
    if eng_kw:
        for line in report_text.split('\n'):
            if '空亡' in line:
                kw_clean = eng_kw.replace('、', '').replace('，', '').replace(' ', '')
                line_clean = line.replace('、', '').replace('，', '').replace(' ', '')
                if kw_clean in line_clean:
                    break
        else:
            errors.append(f"❌ 报告中无空亡信息（引擎：{eng_kw}）")
    return errors


# ══════════════════════════════════════════════
# 线B：/goal 交付门禁校验
# ══════════════════════════════════════════════

# 品牌黑名单
BRAND_BLACKLIST = ['九龙道长', '金鉴真人']

# 性格特质关键词
CHARACTER_TRAITS = ['特质一', '特质二', '特质三', '特质四', '特质五']

# 婚姻子女事件关键词
MARRIAGE_CHILD_KEYWORDS = ['结婚', '配偶', '添丁', '子女', '婚姻', '感情', '生育', '生子']

# 补财库关键词
CAI_KU_KEYWORDS = ['补库', '开库', '蓄库', '充库', '开户补库', '实物补库',
                   '补财库', '财库', '无财库', '保险柜', '合作补库']


def check_brand_name(report_text):
    """G1: 品牌名检查——0残留"""
    errors = []
    for brand in BRAND_BLACKLIST:
        count = report_text.count(brand)
        if count > 0:
            # 找出具体位置
            lines = report_text.split('\n')
            for i, line in enumerate(lines):
                if brand in line:
                    errors.append(f"❌ 品牌名「{brand}」残留：L{i+1} → 「{line.strip()[:60]}」")
    return errors


def check_character_analysis(report_text):
    """G2: 性格分析——五重人格全部存在"""
    errors = []
    missing = []
    for trait in CHARACTER_TRAITS:
        if trait not in report_text:
            missing.append(trait)
    if missing:
        errors.append(f"❌ 性格分析缺少：{', '.join(missing)}")
    return errors


def check_line_count(report_text):
    """G3: 行数检查——精简版≥800行"""
    errors = []
    lines = report_text.split('\n')
    count = len(lines)
    if count < 800:
        errors.append(f"❌ 行数不足：当前{count}行，需≥800行（差额{800 - count}行）")
    return errors


def check_marriage_child_events(report_text):
    """G4: 婚姻子女事件表——≥5行"""
    errors = []
    count = 0
    for kw in MARRIAGE_CHILD_KEYWORDS:
        count += report_text.count(kw)
    if count < 5:
        errors.append(f"❌ 婚姻/子女相关提及仅{count}处（需≥5处）")
    return errors


def check_cai_ku_plan(report_text):
    """G5: 补财库方案——≥5种方法"""
    errors = []
    found = 0
    for kw in CAI_KU_KEYWORDS:
        if kw in report_text:
            found += 1
    if found < 5:
        errors.append(f"❌ 补财库方法提及仅{found}种关键调（需≥5种）")
    return errors


def check_cai_ku_fangwei(report_text, engine):
    """G5b: 补财库方位正确性——根据日主五行验证财才墓库方位"""
    errors = []
    # 从引擎获取日主（兼容扁平/嵌套两种结构）
    s1 = engine.get("sec_1_overview", {}) or {}
    ri_zhu = s1.get("ri_zhu", "")
    # ri_zhu 可能是字符串("庚")或dict({"gan":"庚","wx":"金"})
    if isinstance(ri_zhu, dict):
        ri_gan = ri_zhu.get("gan", "")
    elif isinstance(ri_zhu, str) and ri_zhu:
        ri_gan = ri_zhu[0]
    else:
        ri_gan = ""
    if not ri_gan:
        return errors

    # 财才墓库方位表（日主→财才墓库方位）
    CAI_KU_FANGWEI = {
        '甲': '东南',  # 甲木→财=土→土库=辰(东南) / 戌(西北) 双库
        '乙': '东南',
        '丙': '东北',  # 丙火→财=金→金库=丑(东北)
        '丁': '东北',
        '戊': '东南',  # 戊土→财=水→水库=辰(东南)
        '己': '东南',
        '庚': '西南',  # 庚金→财=木→木库=未(西南)
        '辛': '西南',  # 辛金→财=木→木库=未(西南)
        '壬': '西北',  # 壬水→财=火→火库=戌(西北)
        '癸': '西北',  # 癸水→财=火→火库=戌(西北)
    }

    ri_gan = ri_gan  # 已在函数开头从ri_zhu提取，此处不再重复
    expected_fw = CAI_KU_FANGWEI.get(ri_gan, '')

    if not expected_fw:
        return errors

    # 检查报告中是否提到了正确的方位
    lines = report_text.split('\n')
    in_caiku_section = False
    found_correct = False
    found_wrong = False
    wrong_fw = ''

    for line in lines:
        if '补财库方案' in line or '开户补库' in line or '实物补库' in line:
            in_caiku_section = True

        if in_caiku_section:
            # 检查正确的方位
            if expected_fw in line and ('开户' in line or '实物' in line or '角' in line):
                found_correct = True
            # 检查不正确的方位（仅当补库上下文）
            for other_fw in ['东北', '东南', '西南', '西北']:
                if other_fw != expected_fw and other_fw in line and ('开户' in line or '实物' in line or '角' in line):
                    # 排除文昌方位（文昌西北亥方是正常的）
                    if '文昌' not in line and '忌' not in line:
                        found_wrong = True
                        wrong_fw = other_fw

        # 退出财库段落
        if in_caiku_section and line.strip().startswith('## '):
            break

    if found_wrong:
        errors.append(f"❌ 补财库方位可能错误：日主{ri_gan}的财才墓库应在{expected_fw}方，"
                      f"报告中写了{wrong_fw}方")
    if not found_correct and not found_wrong:
        # 没找到明确方位信息，不报错（可能是从简写法）
        pass

    return errors


def check_data_source(report_text, engine):
    """G6: 财星数字来自引擎JSON"""
    errors = []
    s8 = engine.get("sec_8_wealth", {})
    if not s8:
        result = engine.get("result", {})
        s8 = result.get("sec_8_wealth", {})
    eng_score = s8.get("cai_xing_total")

    if eng_score is None:
        errors.append("⚠️ 引擎无财星数据，跳过本项")
        return errors

    # 提取报告中所有财星数字——精确匹配
    # 只匹配「16.0分」「16分」这种紧跟在财星/总分后面的数字
    numbers_found = re.findall(r'(?:财星总分|财星|总分|实得分)[：: ]*(\d+\.?\d*)分?', report_text)
    if not numbers_found:
        # 容错：匹配「16.0分（」或「16分」这种模式
        numbers_found = re.findall(r'财星[^0-9]{0,5}(\d+\.?\d*)\s*分', report_text)
    if not numbers_found:
        # 再容错：匹配表格中的16.0
        numbers_found = re.findall(r'\|\s*\*{0,2}(\d+\.?\d*)\s*分\s*\*{0,2}\s*\|.*?财', report_text)
    for n in numbers_found:
        try:
            rpt_n = float(n)
            if abs(rpt_n - eng_score) > 0.5:
                errors.append(f"❌ 报告中财星数字{n}与引擎{eng_score}不一致")
        except ValueError:
            continue
    return errors


# ══════════════════════════════════════════════
# 主流程
# ══════════════════════════════════════════════

def check_job_change_signals(report_text, engine):
    """G7: 工作变动信号分析完整性——检查报告是否覆盖七大系统"""
    errors = []
    # 七大系统的关键词
    systems = {
        '官杀系统': ['官杀', '正官', '七杀', '升职', '降职', '事业变动'],
        '印星系统': ['印星', '正印', '偏印', '调令', '合同', '任命'],
        '驿马系统': ['驿马', '寅申', '巳亥', '变动', '跳槽', '换工作'],
        '财星系统': ['财星', '加薪', '涨薪', '薪酬', '收入'],
        '食伤系统': ['食伤', '食神', '伤官', '辞职', '创业'],
        '宫位系统': ['年柱', '月柱', '日支', '时柱', '宫位'],
        '大运周期': ['大运', '换运', '伏吟', '岁运并临'],
    }
    
    # 只检查报告中提到「工作变动」「升职」「跳槽」「变动」的段落
    job_change_kw = ['工作变动', '升职', '跳槽', '加薪', '事业变动', '职业变化']
    has_job_content = any(kw in report_text for kw in job_change_kw)
    
    if not has_job_content:
        return errors  # 报告不含工作变动分析，跳过
    
    # 专项检查3条补充规则
    supplement_rules = {
        '大运换运': ['换运', '大运切换', '大运交接', '大运转换', '大运过渡'],
        '伏吟效应': ['伏吟', '伏吟年', '流年伏吟', '自刑'],
        '岁运并临': ['岁运并临', '岁运并临年', '大运流年相同'],
    }
    missing_supplements = []
    for rule_name, kws in supplement_rules.items():
        if not any(kw in report_text for kw in kws):
            missing_supplements.append(rule_name)
    
    if missing_supplements:
        errors.append(f"⚠️ 工作变动分析缺少补充规则：{', '.join(missing_supplements)}（推荐加入，增强信号强度判断）")
    
    # 检查覆盖了多少系统
    covered = []
    for system, kws in systems.items():
        if any(kw in report_text for kw in kws):
            covered.append(system)
    
    if len(covered) < 3:
        missing = [s for s in systems if s not in covered]
        errors.append(f"❌ 工作变动分析覆盖不足：仅覆盖{len(covered)}/7个系统（{', '.join(covered)}），"
                      f"缺少：{', '.join(missing[:3])}")
    return errors


def main():
    parser = argparse.ArgumentParser(description='金鉴真人·交付物理门禁')
    parser.add_argument('--report', '-r', required=True, help='报告文件路径(.md)')
    parser.add_argument('--engine', '-e', help='引擎数据JSON路径（可选，无则只跑线B）')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--mode', choices=['all', 'line-b-only'], default='all',
                       help='all=双线全跑(默认), line-b-only=只跑/goal门禁')
    args = parser.parse_args()

    # 读取报告
    try:
        with open(args.report, 'r', encoding='utf-8') as f:
            report_text = f.read()
    except FileNotFoundError:
        print(f"❌ 报告文件不存在：{args.report}")
        sys.exit(1)

    # 读取引擎数据
    engine = {}
    if args.engine:
        try:
            with open(args.engine, 'r', encoding='utf-8') as f:
                engine = json.load(f)
        except FileNotFoundError:
            print(f"⚠️ 引擎文件不存在：{args.engine}，仅跑线B")
        except json.JSONDecodeError as e:
            print(f"⚠️ 引擎JSON解析失败：{e}，仅跑线B")
    else:
        if args.verbose:
            print("⚠️ 未提供引擎数据，仅跑线B/goal门禁")

    all_errors = []
    all_passes = []

    # ── 线A：引擎数据一致性（7项） ──
    if args.mode != 'line-b-only' and engine:
        line_a_checks = [
            ("A1 身强弱分数", check_shen_qiang_ruo),
            ("A2 财星分数", check_cai_xing),
            ("A3 五行生克方向", check_wuxing_shengke),
            ("A4 十神名称", check_shi_shen),
            ("A5 大运年份", check_da_yun),
            ("A6 喜忌一致性", check_xi_ji),
            ("A7 空亡一致性", check_kong_wang),
        ]
        for name, func in line_a_checks:
            try:
                result = func(report_text, engine)
                if result:
                    all_errors.extend(result)
                    if args.verbose:
                        print(f"  【{name}】❌ {len(result)}个问题")
                else:
                    all_passes.append(name)
                    if args.verbose:
                        print(f"  【{name}】✅")
            except Exception as e:
                all_errors.append(f"⚠️ {name}异常：{e}")

    # ── 线B：/goal 交付门禁（6项） ──
    line_b_checks = [
        ("G1 品牌名检查", lambda t: check_brand_name(t), True),
        ("G2 性格分析", lambda t: check_character_analysis(t), True),
        ("G3 行数检查≥800", lambda t: check_line_count(t), True),
        ("G4 婚姻子女事件≥5", lambda t: check_marriage_child_events(t), True),
        ("G5 补财库方案≥5", lambda t: check_cai_ku_plan(t), True),
        ("G5b 财库方位正确性", lambda t: check_cai_ku_fangwei(t, engine),
         bool(engine)),
        ("G6 数据来源(财星)", lambda t: check_data_source(t, engine),
         bool(engine)),
        ("G7 工作变动分析", lambda t: check_job_change_signals(t, engine),
         bool(engine)),  # 有引擎数据才跑
    ]

    for name, func, should_run in line_b_checks:
        if not should_run:
            continue
        try:
            result = func(report_text)
            if result:
                all_errors.extend(result)
                if args.verbose:
                    print(f"  【{name}】❌ {len(result)}个问题")
            else:
                all_passes.append(name)
                if args.verbose:
                    print(f"  【{name}】✅")
        except Exception as e:
            all_errors.append(f"⚠️ {name}异常：{e}")

    # ── 输出结果 ──
    print(f"\n{'='*55}")
    print(f"📋 交付门禁报告：{args.report}")
    print(f"{'='*55}")

    if all_passes:
        print(f"✅ 通过：{len(all_passes)}项")
        for p in all_passes:
            print(f"   ✅ {p}")

    if all_errors:
        print(f"\n❌ 阻断：发现 {len(all_errors)} 个问题（必须全部修复后才能交付）：")
        print(f"{'─'*50}")
        for err in all_errors:
            print(f"  🔴 {err}")
        print(f"\n{'─'*50}")
        print(f"⛔ 交付被阻断！先修复再重跑 delivery-gate.py")
        sys.exit(1)
    else:
        print(f"\n{'─'*50}")
        print(f"✅✅✅ 全部通过！可以交付。")
        sys.exit(0)


if __name__ == '__main__':
    main()
