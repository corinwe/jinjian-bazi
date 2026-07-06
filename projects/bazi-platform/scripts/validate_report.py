#!/usr/bin/env python3
"""
金鉴真人·八字报告验证脚本 v1.1
用法：python3 validate_report.py <报告文件路径> <人物姓名>
"""
import json, re, sys

DATA_SOURCE = "/root/.hermes/profiles/jinjian-zhenren/scripts/family_bazi_data.json"

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
    # **八字：** 庚申 癸未 辛亥 辛卯 或 八字：庚申 癸未 辛亥 辛卯 等
    # 在头部元数据中或在表格中
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
    
    # 身强弱：有各种写法
    # **身强身弱** | **身强（64分）** 或 | 8 | **身强身弱** | **64分（身强）** |
    # 或 **身强（64.0分）**
    patterns_s = [
        r'\*\*身强身弱\*\*\s*[|]\s*\*\*([\d.]+)分\*\*',
        r'\*\*身强身弱\*\*\s*[|]\s*\*\*身[强弱]+\s*[(（]([\d.]+)分',
        r'\*\*身强身弱\*\*\s*[|]\s*\*\*([\d.]+)分',
        r'身强身弱[|]\s*\*\*([\d.]+)分',
        r'身强身弱[：:]\s*\*\*([\d.]+)分',
        r'身强身弱[：:]\s*([\d.]+)分',
        r'\*\*身强\*\*\s*[（(]([\d.]+)分',
        r'\*\*身弱\*\*\s*[（(]([\d.]+)分',
        r'[\u4e00-\u9fff]+[(（]([\d.]+)分[)）]',
    ]
    for p in patterns_s:
        m = re.search(p, text)
        if m:
            val = m.group(1)
            try:
                nums['身强弱'] = float(val)
                break
            except:
                pass
    
    # 财星：| 13 | **财星分数** | **30.8分（...）** |
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
    
    # 八字
    src_bazi = person['八字'].replace(' ','')
    if '八字' in nums:
        rpt_bazi = nums['八字'].replace(' ','')
        if rpt_bazi != src_bazi:
            errors.append(f"❌ 八字不一致\n   报告: {nums['八字']}\n   数据源: {person['八字']}")
        else:
            print(f"  ✅ 八字一致")
    else:
        warnings.append(f"⚠️ 未提取到八字（期望: {person['八字']}）")
    
    # 身强弱
    src_score = person['身强弱']['总分']
    if '身强弱' in nums:
        if abs(nums['身强弱'] - src_score) > 0.5:
            errors.append(f"❌ 身强弱:{nums['身强弱']}分 vs 数据源:{src_score}分")
        else:
            print(f"  ✅ 身强弱一致: {src_score}分")
    else:
        warnings.append(f"⚠️ 未提取到身强弱（期望: {src_score}分）")
    
    # 财星
    src_wealth = person['财星']['总分']
    if '财星' in nums:
        if abs(nums['财星'] - src_wealth) > 0.5:
            errors.append(f"❌ 财星:{nums['财星']}分 vs 数据源:{src_wealth}分")
        else:
            print(f"  ✅ 财星一致: {src_wealth}分")
    else:
        warnings.append(f"⚠️ 未提取到财星（期望: {src_wealth}分）")
    
    # 起运年龄
    src_qiyun = person['大运']['起运年龄']
    if '起运年龄' in nums:
        if abs(nums['起运年龄'] - src_qiyun) > 0.5:
            errors.append(f"❌ 起运:{nums['起运年龄']}岁 vs 数据源:{src_qiyun}岁")
        else:
            print(f"  ✅ 起运年龄一致: {src_qiyun}岁")
    else:
        warnings.append(f"⚠️ 未提取到起运年龄（期望: {src_qiyun}岁）")
    
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
        print(f"\n✅ 验证通过！所有数字与数据源一致")
