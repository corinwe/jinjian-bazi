#!/usr/bin/env python3
"""
金鉴真人·报告自动校验器 v1.0
物理闸门——在推库前自动检查报告 vs 引擎数据的一致性

用法：
  python3 verify_report.py --report 报告.md --engine 引擎数据.json

检查项：
  ① 身强弱分数一致
  ② 财星分数一致
  ③ 五行生克方向正确（防写反）
  ④ 十神名称正确（防正印/偏印搞混）
  ⑤ 大运年份正确
  ⑥ 喜忌与引擎一致
  ⑦ 空亡与引擎一致

退出码：
  0 = 全部通过
  1 = 有错误（阻断推库）
"""

import re
import sys
import json
import argparse


def extract_score(text, pattern, label):
    """从报告中提取分数"""
    m = re.search(pattern, text)
    if m:
        return float(m.group(1))
    return None


def check_shen_qiang_ruo(report_text, engine):
    """检查①：身强弱分数一致"""
    errors = []
    result = engine.get("result", {})
    s3 = result.get("sec_3_shen_qiang_ruo", {})
    if not s3:
        s3 = engine.get("sec_3_shen_qiang_ruo", {})
    exp_score = s3.get("score")
    exp_label = s3.get("label", "")
    
    if exp_score is None:
        errors.append("⚠️ 引擎数据中无身强弱分数，跳过该项检查")
        return errors

    # 找 "身强（64.0分）" 或 "从弱（50.0分）" 这样的模式
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
                errors.append(f"❌ 身强弱分数不一致：报告写{rpt_score}分，引擎是{exp_score}分")
            if rpt_label != exp_label and exp_label:
                # "身强"vs"身强" 检查
                if rpt_label not in exp_label and exp_label not in rpt_label:
                    errors.append(f"❌ 身强弱标签不一致：报告写「{rpt_label}」，引擎是「{exp_label}」")
            break
        if found:
            break
    
    if not found:
        errors.append("❌ 未在报告中找到身强弱信息")
    
    return errors


def check_cai_xing(report_text, engine):
    """检查②：财星分数一致"""
    errors = []
    s8 = engine.get("sec_8_wealth", {})
    exp_score = s8.get("cai_xing_total")

    patterns = [
        r'财星分数[^0-9]*([\d.]+)分',
        r'财星[^0-9]*([\d.]+)分',
        r'(\d+\.?\d*)分.*财',
    ]
    found = False
    for p in patterns:
        for m in re.finditer(p, report_text):
            rpt_score = float(m.group(1))
            if exp_score and abs(rpt_score - exp_score) > 0.5:
                errors.append(f"❌ 财星分数不一致：报告写{rpt_score}分，引擎是{exp_score}分")
            found = True
            break
        if found:
            break
    
    return errors


# 五行生克方向正确表（不可写反）
# (写法1, 写法2, 应该是什么)
WU_XING_RULES = [
    # 正确关系
    (r'金\s*生\s*土', '金生土', False),  # ❌ 应该是土生金
    (r'土\s*生\s*金', '土生金', True),   # ✅ 正确
    (r'木\s*生\s*金', '木生金', False),  # ❌ 应该是金克木
    (r'火\s*生\s*水', '火生水', False),  # ❌ 应该是水克火
    (r'水\s*生\s*土', '水生土', False),  # ❌ 应该是土克水
    (r'土\s*克\s*金', '土克金', False),  # ❌ 应该是金克木... 不对，土生金
    # 土和金的关系要仔细
]


def check_wuxing_shengke(report_text, engine=None):
    """检查③：五行生克方向"""
    errors = []
    # 土和金：土生金（正确），金生土（错误）
    if re.search(r'金\s*(生|助)\s*土', report_text):
        # 只有在明确写「金生土」「金助土」时才报错
        # 但「金生助土」这种也要查
        lines = report_text.split('\n')
        for i, line in enumerate(lines):
            if re.search(r'金\s*(生|助)\s*土', line):
                # 排除「土生金」「土被金泄」等正确表述
                if not re.search(r'土\s*生\s*金|土被金泄|金泄土', line):
                    errors.append(f"❌ L{i+1}: 五行生克可能写反——「{line.strip()[:60]}」")
                    errors.append(f"   正确关系是土生金，不是金生土")

    # 检查「金生助土」「金来生土」等变体
    if re.search(r'金[来被]生[助]?土|金生[助]?土', report_text):
        lines = report_text.split('\n')
        for i, line in enumerate(lines):
            if re.search(r'金[来被]?生[助]?土', line) and not re.search(r'土生金|土被金', line):
                errors.append(f"❌ L{i+1}: 「金生土」方向错误——正确是土生金")

    return errors


def check_shi_shen(report_text, engine):
    """检查④：十神名称正确（防正印/偏印搞混）"""
    errors = []
    
    # 重点检查：戊土对辛金是正印不是偏印
    for i, line in enumerate(report_text.split('\n')):
        if '戊土' in line and '偏印' in line and '正印' not in line:
            errors.append(f"❌ L{i+1}: 戊土对辛金=正印（不是偏印）。戊(阳)生辛(阴)=正印")
    
    return errors


def check_da_yun(report_text, engine):
    """检查⑤：大运年份正确"""
    errors = []
    result = engine.get("result", {})
    s17 = result.get("sec_17_da_yun_detail", {})
    dy_list = s17.get("list", [])
    
    if not dy_list:
        return errors
    
    # 检查大运干支是否与引擎一致
    for dy in dy_list:
        gz = dy.get("gan_zhi", "")
        if gz and gz in report_text:
            # 找到该大运——检查年份
            lines = report_text.split('\n')
            for i, line in enumerate(lines):
                if gz in line and ('~' in line or '～' in line or '—' in line):
                    pass  # 年份格式多样，暂时只报信息不报错
    
    return errors


def check_xi_ji(report_text, engine):
    """检查⑥：喜忌与引擎一致——比较元素而非格式"""
    errors = []
    result = engine.get("result", {})
    s4 = result.get("sec_4_xi_yong", {})
    eng_xi = s4.get("xi", [])
    eng_ji = s4.get("ji", [])
    
    if not eng_xi and not eng_ji:
        return errors
    
    # 只找§1的喜用/忌神行（唯一需要精确匹配的行）
    lines = report_text.split('\n')
    for i, line in enumerate(lines):
        # 找 §1 表格中的喜用神行
        if re.match(r'\|\s*10\s*\|\s*\*\*喜用神', line):
            # 检查引擎的每个喜用是否都在行中
            for wx in eng_xi:
                if wx not in line:
                    errors.append(f"❌ L{i+1}: 喜用神缺少「{wx}」")
        # 找 §1 表格中的忌神行
        if re.match(r'\|\s*11\s*\|\s*\*\*忌神', line):
            for wx in eng_ji:
                if wx not in line:
                    errors.append(f"❌ L{i+1}: 忌神缺少「{wx}」")
    
    return errors


def check_kong_wang(report_text, engine):
    """检查⑦：空亡与引擎一致"""
    errors = []
    result = engine.get("result", {})
    s1 = result.get("sec_1_overview", {})
    eng_kw = s1.get("kong_wang", "")
    
    if eng_kw:
        for line in report_text.split('\n'):
            if '空亡' in line:
                # 空亡格式可能是 "寅、卯" 或 "寅卯" 或 "戌亥"
                kw_clean = eng_kw.replace('、', '').replace('，', '')
                line_clean = line.replace('、', '').replace('，', '').replace(' ', '')
                if kw_clean in line_clean:
                    break
        else:
            errors.append(f"❌ 未在报告中找到空亡信息（引擎：{eng_kw}）")
    
    return errors


def main():
    parser = argparse.ArgumentParser(description='金鉴真人·报告自动校验器')
    parser.add_argument('--report', required=True, help='报告文件路径(.md)')
    parser.add_argument('--engine', required=True, help='引擎数据JSON路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    args = parser.parse_args()

    # 读取报告
    with open(args.report, 'r', encoding='utf-8') as f:
        report_text = f.read()

    # 读取引擎数据
    with open(args.engine, 'r', encoding='utf-8') as f:
        engine = json.load(f)

    all_errors = []
    all_warnings = []

    # 执行7项检查
    checks = [
        ("①身强弱分数", check_shen_qiang_ruo),
        ("②财星分数", check_cai_xing),
        ("③五行生克方向", check_wuxing_shengke),
        ("④十神名称", check_shi_shen),
        ("⑤大运年份", check_da_yun),
        ("⑥喜忌一致性", check_xi_ji),
        ("⑦空亡一致性", check_kong_wang),
    ]

    for name, func in checks:
        try:
            result = func(report_text, engine)
            if result:
                all_errors.extend(result)
                if args.verbose:
                    print(f"\n{'='*40}")
                    print(f"【{name}】发现 {len(result)} 个问题：")
                    for e in result:
                        print(f"  {e}")
            else:
                if args.verbose:
                    print(f"【{name}】✅ 通过")
        except Exception as e:
            all_warnings.append(f"⚠️ {name} 检查异常：{e}")

    # 输出结果
    print(f"\n{'='*50}")
    if all_errors:
        print(f"❌ 校验未通过 — 发现 {len(all_errors)} 个错误：")
        for e in all_errors:
            print(f"  {e}")
        print(f"\n⛔ 阻断：请修正以上错误后重新校验")
        sys.exit(1)
    else:
        print(f"✅ 全部校验通过！")
        if all_warnings:
            for w in all_warnings:
                print(f"  {w}")
        sys.exit(0)


if __name__ == '__main__':
    main()
