#!/usr/bin/env python3
"""
金鉴真人·八字报告验证脚本 v1.2
用法：python3 validate_report.py <报告文件路径> <人物姓名>

v1.2新增：喜忌用神逻辑自检（2026-06-20子源案例触发）
"""
import json, re, sys

DATA_SOURCE = "/root/.hermes/profiles/jinjian-zhenren/scripts/family_bazi_data.json"

# 身强弱 → 喜用五行映射规则
XIYONG_RULES = {
    "身强": {"xiyong": ["水", "土", "金"], "jishen": ["火", "木"], "desc": "克泄耗（财官食）"},
    "偏强": {"xiyong": ["水", "土", "金"], "jishen": ["火", "木"], "desc": "克泄耗（财官食）"},
    "中和偏强": {"xiyong": ["水", "土", "金"], "jishen": ["火", "木"], "desc": "克泄耗（财官食）"},
    "身弱": {"xiyong": ["木", "火"], "jishen": ["水", "土", "金"], "desc": "生扶（印比）"},
    "偏弱": {"xiyong": ["木", "火"], "jishen": ["水", "土", "金"], "desc": "生扶（印比）"},
    "中和偏弱": {"xiyong": ["木", "火"], "jishen": ["水", "土", "金"], "desc": "生扶（印比）"},
    "中和": {"xiyong": ["水", "土", "金"], "jishen": ["火", "木"], "desc": "中庸偏强侧按克泄耗"},
    "从弱": {"xiyong": ["所有五行"], "jishen": [], "desc": "从弱反为强，所有五行皆喜用"},
    "从强": {"xiyong": ["木", "火"], "jishen": ["水", "土", "金"], "desc": "从强反为弱，喜印比生扶"},
}

# 五行中文字符统一
WUXING_MAP = {
    "金": "金", "银": "金",
    "木": "木",
    "水": "水",
    "火": "火",
    "土": "土",
    "财": "金", "才": "金",
    "官": "水", "杀": "水",
    "印": "木", "枭": "木",
    "食": "土", "伤": "土",
    "比": "火", "劫": "火",
}


def load_data():
    with open(DATA_SOURCE, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_person(data, name):
    for p in data:
        if p['姓名'] == name:
            return p
    return None


def extract(text):
    """从报告中提取关键数字"""
    nums = {}

    # 八字：各种格式
    patterns_8 = [
        r'\*\*八字[：:]\*\*\s*([\u4e00-\u9fff]+\s+[\u4e00-\u9fff]+\s+[\u4e00-\u9fff]+\s+[\u4e00-\u9fff]+)',
        r'八字[：:]\s*([\u4e00-\u9fff]+\s+[\u4e00-\u9fff]+\s+[\u4e00-\u9fff]+\s+[\u4e00-\u9fff]+)',
        r'\*\*四柱八字\*\*[|]\s*([\u4e00-\u9fff]+\s+[\u4e00-\u9fff]+\s+[\u4e00-\u9fff]+\s+[\u4e00-\u9fff]+)',
        r'四柱八字[|]\s*([\u4e00-\u9fff]+\s+[\u4e00-\u9fff]+\s+[\u4e00-\u9fff]+\s+[\u4e00-\u9fff]+)',
    ]
    for p in patterns_8:
        m = re.search(p, text)
        if m:
            nums['八字'] = m.group(1).strip()
            break

    # 身强弱分数
    patterns_s = [
        r'\*\*身强身弱\*\*\s*[|]\s*\*\*([\d.]+)分',
        r'\*\*身强身弱\*\*\s*[|]\s*\*\*身[强弱]+\s*[（(]([\d.]+)分',
        r'\*\*身强身弱\*\*\s*[|]\s*\*\*([\d.]+)分',
        r'身强身弱[|]\s*\*\*([\d.]+)分',
        r'身强身弱[：:]\s*\*\*([\d.]+)分',
        r'身强身弱[：:]\s*([\d.]+)分',
        r'\*\*身强\*\*\s*[（(]([\d.]+)分',
        r'\*\*身弱\*\*\s*[（(]([\d.]+)分',
        r'[\u4e00-\u9fff]+[（(]([\d.]+)分[)）]',
    ]
    for p in patterns_s:
        m = re.search(p, text)
        if m:
            try:
                nums['身强弱'] = float(m.group(1))
                break
            except:
                pass

    # 身强弱等级文本（如 "身强" "中和" "身弱" "中和偏强"）
    patterns_level = [
        r'\*\*身强身弱\*\*\s*[|]\s*\*\*(\S+?)（([\d.]+)分）',
        r'\*\*身强身弱\*\*\s*[|]\s*\*\*(\S+?)\(([\d.]+)分\)',
        r'身强身弱[|]\s*\*\*(\S+?)（([\d.]+)分）',
    ]
    for p in patterns_level:
        m = re.search(p, text)
        if m:
            level_text = m.group(1).strip()
            if "身强" in level_text and "偏" in level_text:
                nums['身强弱等级'] = "偏强"
            elif "身强" in level_text:
                nums['身强弱等级'] = "身强"
            elif "身弱" in level_text and "偏" in level_text:
                nums['身强弱等级'] = "偏弱"
            elif "身弱" in level_text:
                nums['身强弱等级'] = "身弱"
            elif "中和" in level_text:
                nums['身强弱等级'] = "中和"
            elif "从弱" in level_text:
                nums['身强弱等级'] = "从弱"
            elif "从强" in level_text:
                nums['身强弱等级'] = "从强"
            break

    # 如果没提取到等级，用分数推断
    if '身强弱' in nums and '身强弱等级' not in nums:
        score = nums['身强弱']
        if score >= 60:
            nums['身强弱等级'] = "身强"
        elif score >= 55:
            nums['身强弱等级'] = "中和偏强"
        elif score >= 40:
            nums['身强弱等级'] = "中和"
        elif score == 50 and '从弱' in text:
            nums['身强弱等级'] = "从弱"
        else:
            nums['身强弱等级'] = "身弱"

    # 喜用神（取表格第10行中的五行顺序）
    # 格式：| 10 | **喜用神（排序）** | 🟢 💧水（官杀）> 🌳木（印星） |
    pattern_xi = r'\*\*喜用神[^|]*\*\*\s*[|]\s*(?:🟢\s*)?[^>]*?>?\s*([^\|]+)'
    m = re.search(pattern_xi, text)
    if not m:
        # 尝试更宽松的匹配
        pattern_xi2 = r'喜用神[^|]*\|\s*[^\|🟢🔴]*(?:🟢\s*)?([^🔴\|]*)'
        m = re.search(pattern_xi2, text)
    if m:
        nums['喜用神原文'] = m.group(1).strip()
        # 提取五行字
        found = []
        for ch in ['水', '火', '木', '金', '土']:
            if ch in nums['喜用神原文']:
                found.append(ch)
        nums['喜用神五行'] = found

    # 忌神（取表格第11行）
    pattern_ji = r'\*\*忌神[^|]*\*\*\s*[|]\s*(?:🔴\s*)?([^\|]+)'
    m = re.search(pattern_ji, text)
    if not m:
        pattern_ji2 = r'忌神[^|]*\|\s*[^\|🔴🟢]*(?:🔴\s*)?([^🟢\|]*)'
        m = re.search(pattern_ji2, text)
    if m:
        nums['忌神原文'] = m.group(1).strip()
        found = []
        for ch in ['水', '火', '木', '金', '土']:
            if ch in nums['忌神原文']:
                found.append(ch)
        nums['忌神五行'] = found

    # 财星
    patterns_w = [
        r'\*\*财星分数\*\*\s*[|]\s*\*\*([\d.]+)分',
        r'财星分数[|]\s*\*\*([\d.]+)分',
        r'财星分数[：:]\s*\*\*([\d.]+)分',
        r'财星分数[：:]\s*([\d.]+)分',
        r'财星总分[：:]\s*\*\*([\d.]+)分',
        r'财星总分[：:]\s*([\d.]+)分',
    ]
    for p in patterns_w:
        m = re.search(p, text)
        if m:
            try:
                nums['财星'] = float(m.group(1))
                break
            except:
                pass

    # 起运年龄
    patterns_q = [
        r'\*\*起运年龄\*\*\s*[|]\s*\*\*([\d.]+)岁',
        r'起运年龄[|]\s*\*\*([\d.]+)岁',
        r'起运年龄[：:]\s*\*\*([\d.]+)岁',
        r'起运[：:]\s*([\d.]+)岁',
        r'起运[：:]\s*\*+([\d.]+)岁',
    ]
    for p in patterns_q:
        m = re.search(p, text)
        if m:
            try:
                nums['起运年龄'] = float(m.group(1))
                break
            except:
                pass

    return nums


def check_xiyong_jishen(nums):
    """喜忌用神逻辑自检"""
    problems = []

    level = nums.get('身强弱等级', '')
    score = nums.get('身强弱', None)
    xiyong = nums.get('喜用神五行', [])
    jishen = nums.get('忌神五行', [])

    if not level:
        return ["⚠️ 无法推断身强弱等级，跳过喜忌用神自检"]
    if not xiyong and not jishen:
        return ["⚠️ 未提取到喜用神/忌神数据，跳过自检"]

    # 查找匹配规则
    rule = None
    for key, val in XIYONG_RULES.items():
        if key in level:
            rule = val
            break

    if not rule:
        return [f"⚠️ 未找到身强弱「{level}」对应的喜忌规则"]

    expected_xi = set(rule['xiyong'])
    expected_ji = set(rule['jishen'])
    problems_list = []

    # 检查喜用神
    if xiyong:
        if rule['xiyong'] == ["所有五行"]:
            # 从弱格特殊处理
            pass
        else:
            for w in xiyong:
                if w not in expected_xi:
                    problems_list.append(
                        f"❌ 喜用神包含「{w}」，但身强弱「{level}」({score}分)的喜用应为{rule['desc']}"
                    )

    # 检查忌神
    if jishen and rule['jishen']:
        for w in jishen:
            if w not in expected_ji:
                problems_list.append(
                    f"❌ 忌神包含「{w}」，但身强弱「{level}」({score}分)的忌神不应包含{w}"
                )

    if not problems_list:
        problems_list.append(f"✅ 喜忌用神逻辑自洽——身强弱{level} ({score}分)，喜用={rule['desc']}")

    return problems_list


def validate(report_path, person_name):
    data = load_data()
    person = find_person(data, person_name)
    if not person:
        return [f"❌ 数据源中未找到「{person_name}」"], []

    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except:
        return [f"❌ 无法读取文件: {report_path}"], []

    nums = extract(text)
    errors = []
    warnings = []

    print(f"\n{'='*60}")
    print(f"金鉴真人·八字报告验证 v1.2")
    print(f"人物: {person_name}")
    print(f"{'='*60}\n")

    # 1. 八字
    src_bazi = person['八字'].replace(' ', '')
    if '八字' in nums:
        rpt_bazi = nums['八字'].replace(' ', '')
        if rpt_bazi != src_bazi:
            errors.append(f"❌ 八字不一致\n   报告: {nums['八字']}\n   数据源: {person['八字']}")
        else:
            print(f"  ✅ 八字一致")
    else:
        warnings.append(f"⚠️ 未提取到八字（期望: {person['八字']}）")

    # 2. 身强弱
    src_score = person['身强弱']['总分']
    if '身强弱' in nums:
        if abs(nums['身强弱'] - src_score) > 0.5:
            errors.append(f"❌ 身强弱:{nums['身强弱']}分 vs 数据源:{src_score}分")
        else:
            print(f"  ✅ 身强弱一致: {src_score}分")
    else:
        warnings.append(f"⚠️ 未提取到身强弱（期望: {src_score}分）")

    # 3. 财星
    src_wealth = person['财星']['总分']
    if '财星' in nums:
        if abs(nums['财星'] - src_wealth) > 0.5:
            errors.append(f"❌ 财星:{nums['财星']}分 vs 数据源:{src_wealth}分")
        else:
            print(f"  ✅ 财星一致: {src_wealth}分")
    else:
        warnings.append(f"⚠️ 未提取到财星（期望: {src_wealth}分）")

    # 4. 起运年龄
    src_qiyun = person['大运']['起运年龄']
    if '起运年龄' in nums:
        if abs(nums['起运年龄'] - src_qiyun) > 0.5:
            errors.append(f"❌ 起运:{nums['起运年龄']}岁 vs 数据源:{src_qiyun}岁")
        else:
            print(f"  ✅ 起运年龄一致: {src_qiyun}岁")
    else:
        warnings.append(f"⚠️ 未提取到起运年龄（期望: {src_qiyun}岁）")

    # 5. 🚨 喜忌用神逻辑自检（v1.2新增）
    print(f"  → 身强弱等级: {nums.get('身强弱等级', '未知')}")
    if '喜用神五行' in nums:
        print(f"  → 喜用神: {nums.get('喜用神原文', '')}")
    if '忌神五行' in nums:
        print(f"  → 忌神: {nums.get('忌神原文', '')}")
    xiyong_results = check_xiyong_jishen(nums)
    for r in xiyong_results:
        if r.startswith("❌"):
            errors.append(r)
        elif r.startswith("✅"):
            print(f"  {r}")
        else:
            warnings.append(r)

    return errors, warnings


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python3 validate_report.py <报告文件路径> <人物姓名>")
        sys.exit(1)

    errors, warnings = validate(sys.argv[1], sys.argv[2])

    if warnings:
        print(f"\n⚠️ 警告 ({len(warnings)}条):")
        for w in warnings:
            print(f"  {w}")

    if errors:
        print(f"\n❌ 错误 ({len(errors)}条):")
        for e in errors:
            print(f"  {e}")
        print(f"\n→ 结论: ❌ 验证不通过——请修正后重试")
        sys.exit(1)
    else:
        print(f"\n✅ 验证通过！所有校验项一致")
