#!/usr/bin/env python3
"""
金鉴真人·大运年份物理约束验证脚本 v1.0
2026-06-24新增·老板令

功能：强制检查报告中所有大运年份与引擎JSON是否一致
用法：python3 bazi-dayun-verify.py <报告路径> <引擎JSON路径> [姓名]
输出：通过/不通过 详细差异列表

物理约束：此脚本必须集成到：
  1. git pre-commit hook（自动触发）
  2. bazi-pipeline.sh --verify（手动触发）
  3. delegate_task子agent返回后强制校验
"""

import json
import re
import sys


def load_engine_data(json_path):
    """从引擎JSON加载大运序列"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    sequences = data.get('大运', {}).get('序列', [])
    if not sequences:
        print("❌ 引擎JSON中无大运序列数据")
        return None
    
    qiyun = data.get('大运', {}).get('起运', '未知')
    qiyun_age = data.get('大运', {}).get('起运年龄', '未知')
    
    engine_dayun = []
    for dy in sequences:
        engine_dayun.append({
            'ganzhi': dy['干支'],
            'start_year': dy['起始年份'],
            'end_year': dy['终止年份'],
            'start_age': dy['起始年龄'],
            'end_age': dy['终止年龄']
        })
    
    return {
        'sequences': engine_dayun,
        'qiyun': qiyun,
        'qiyun_age': qiyun_age
    }


def extract_report_dayun(report_path):
    """从报告中提取所有大运年份引用"""
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    found = []
    lines = content.split('\n')
    
    # 模式A: "甲申  1981~1990" 或 "甲申 1981-1990"（行内直接格式）
    pattern_a = r'([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+(\d{4})\s*[~\-–—]\s*(\d{4})'
    for line in lines:
        matches = re.findall(pattern_a, line)
        for m in matches:
            start, end = int(m[1]), int(m[2])
            if 5 <= end - start <= 15:
                found.append({'ganzhi': m[0], 'start': start, 'end': end})
    
    # 模式B: 表格行 "|壬辰|2016-2025|4-14|" 或 "|壬辰|8~18岁|2020~2029|"
    # 按|拆分，找干支和年份对
    for line in lines:
        if '|' not in line:
            continue
        cells = [re.sub(r'\*\*', '', c).strip() for c in line.split('|') if c.strip()]
        for i, cell in enumerate(cells):
            # 检查是否是干支
            gz_match = re.match(r'^([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])$', cell)
            if not gz_match:
                continue
            gz = gz_match.group(1)
            # 看后面的单元格是否有年份对
            for j in range(i+1, min(i+4, len(cells))):
                year_match = re.match(r'^(\d{4})\s*[~\-–—]\s*(\d{4})$', cells[j])
                if year_match:
                    start, end = int(year_match.group(1)), int(year_match.group(2))
                    if 5 <= end - start <= 15:
                        found.append({'ganzhi': gz, 'start': start, 'end': end})
                    break
    
    # 去重
    seen = set()
    unique = []
    for f in found:
        key = f"{f['ganzhi']}_{f['start']}_{f['end']}"
        if key not in seen:
            seen.add(key)
            unique.append(f)
    
    return unique


def verify_dayun(engine_data, report_refs, name=""):
    """验证报告中大运年份与引擎一致性"""
    engine_seqs = engine_data['sequences']
    
    errors = []
    ok_count = 0
    
    # 构建引擎大运年份表用于校验
    engine_year_pairs = {}
    for seq in engine_seqs:
        key = seq['ganzhi']
        engine_year_pairs[key] = (seq['start_year'], seq['end_year'])
    
    # 检查每个报告引用的大运干支对应的年份
    for ref in report_refs:
        gz = ref['ganzhi']
        if gz in engine_year_pairs:
            expected_start, expected_end = engine_year_pairs[gz]
            if ref['start'] != expected_start or ref['end'] != expected_end:
                errors.append({
                    'ganzhi': gz,
                    'report': (ref['start'], ref['end']),
                    'engine': (expected_start, expected_end),
                    'diff': ref['start'] - expected_start
                })
            else:
                ok_count += 1
    
    return errors, ok_count


def main():
    if len(sys.argv) < 3:
        print("用法: python3 bazi-dayun-verify.py <报告.md> <引擎.json> [姓名]")
        sys.exit(1)
    
    report_path = sys.argv[1]
    json_path = sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else ""
    
    print(f"{'='*60}")
    print(f"  金鉴真人·大运年份物理约束验证")
    if name:
        print(f"  命主: {name}")
    print(f"{'='*60}")
    
    # 加载引擎数据
    engine = load_engine_data(json_path)
    if not engine:
        print("\n❌ 验证失败：无法加载引擎数据")
        sys.exit(1)
    
    print(f"\n引擎起运: {engine['qiyun']} (年龄{engine['qiyun_age']})")
    print(f"引擎大运序列:")
    for seq in engine['sequences']:
        print(f"  {seq['ganzhi']}: {seq['start_year']}~{seq['end_year']} ({seq['start_age']}~{seq['end_age']}岁)")
    
    # 从报告提取大运引用
    report_refs = extract_report_dayun(report_path)
    print(f"\n报告中共发现 {len(report_refs)} 处大运年份引用")
    
    # 验证
    errors, ok_count = verify_dayun(engine, report_refs, name)
    
    # 输出结果
    if not errors:
        print(f"\n✅ 全部 {ok_count} 处大运年份与引擎一致！")
        sys.exit(0)
    else:
        print(f"\n❌ 发现 {len(errors)} 处大运年份错误！")
        print(f"\n{'='*60}")
        print(f"  错误明细")
        print(f"{'='*60}")
        for err in errors:
            print(f"  ❌ {err['ganzhi']}: 报告={err['report'][0]}~{err['report'][1]}, "
                  f"引擎={err['engine'][0]}~{err['engine'][1]}, "
                  f"偏差={err['diff']:+.0f}年")
        
        print(f"\n✅ 正确 {ok_count} 处 | ❌ 错误 {len(errors)} 处")
        print(f"\n⚠️ 请修正报告中大运年份后再推库！")
        sys.exit(2)


if __name__ == '__main__':
    main()
