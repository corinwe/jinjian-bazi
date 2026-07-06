#!/usr/bin/env python3
"""
排盘结果·藏干十神解析（源头校验）
=====================================
用法: 被 bazi-must-run-engine.sh 自动调用
      python3 canggan-parse.py --result <排盘JSON文件路径>

功能:
  1. 输出四柱每个地支的藏干列表
  2. 标注主气对应的十神（对日主）
  3. 标注「易混淆」项（如辛日主午火=七杀非正官）

易混淆对照表（写死的核心防错数据）:
  (辛,午): 七杀⚠️  ← 最容易犯的错误
  (庚,午): 正官✅
  (丙,巳): 比肩⚠️
  (甲,午): 伤官⚠️
"""

import sys
import json

# ── 易混淆对照表（排盘源头校验的核心） ──
CONFUSION_MAP = {
    ('辛', '午'): ('七杀', True),    # ⚠️ 易犯错误：午火=正官
    ('庚', '午'): ('正官', False),
    ('丙', '巳'): ('比肩', True),    # ⚠️ 易犯错误：巳火=劫财
    ('甲', '午'): ('伤官', True),    # ⚠️ 易犯错误：午火=食神
    ('甲', '子'): ('正印', False),
    ('辛', '子'): ('食神', False),
    ('辛', '卯'): ('偏财', False),
    ('辛', '亥'): ('伤官', False),
    ('丙', '子'): ('正官', False),
    ('丙', '辰'): ('食神', False),
    ('丙', '戌'): ('食神', False),
    ('丙', '申'): ('偏财', False),
    ('戊', '午'): ('正印', False),
    ('甲', '申'): ('七杀', False),
    ('甲', '酉'): ('正官', False),
    ('庚', '亥'): ('食神', False),
    ('庚', '未'): ('正印', False),
    ('辛', '未'): ('偏印', False),
    ('辛', '巳'): ('正官', False),
    ('甲', '戌'): ('偏财', False),
    ('乙', '卯'): ('比肩', False),
    ('壬', '子'): ('劫财', False),
    ('甲', '辰'): ('偏财', False),
}

# ── 引擎藏干表 ──
CANG_GAN_TABLE = {
    '子': ['癸'],
    '丑': ['己', '癸', '辛'],
    '寅': ['甲', '丙', '戊'],
    '卯': ['乙'],
    '辰': ['戊', '乙', '癸'],
    '巳': ['丙', '庚', '戊'],
    '午': ['丁', '己'],
    '未': ['己', '丁', '乙'],
    '申': ['庚', '壬', '戊'],
    '酉': ['辛'],
    '戌': ['戊', '辛', '丁'],
    '亥': ['壬', '甲'],
}

def parse_pillar(ri_zhu, pillar_name, gan, zhi):
    """解析一个柱的藏干十神"""
    cang_gans = CANG_GAN_TABLE.get(zhi, ['?'])
    main_qi = cang_gans[0] if cang_gans else '?'
    
    key = (ri_zhu, zhi)
    if key in CONFUSION_MAP:
        ss_name, is_confused = CONFUSION_MAP[key]
    else:
        ss_name = '—'
        is_confused = False
    
    mark = ' ⚠️ 易混淆' if is_confused else ''
    return {
        'pillar': pillar_name,
        'gan': gan,
        'zhi': zhi,
        'cang_gan': '/'.join(cang_gans),
        'main_qi': main_qi,
        'shi_shen': ss_name + mark,
        'is_confused': is_confused,
    }

def main():
    if len(sys.argv) < 2:
        print('用法: python3 canggan-parse.py <排盘JSON文件>', file=sys.stderr)
        sys.exit(1)
    
    with open(sys.argv[1]) as f:
        data = json.load(f)
    
    ri_zhu = data.get('day_pillar', {}).get('gan', '?')
    
    print('')
    print('━━━ 藏干十神解析（源头校验）━━━')
    
    has_confusion = False
    for p_name in ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']:
        p = data.get(p_name, {})
        if not p:
            continue
        result = parse_pillar(ri_zhu, p_name, p.get('gan','?'), p.get('zhi','?'))
        mark = ' ⚠️' if result['is_confused'] else ''
        print(f'  {p_name[:4]}: {result["gan"]}{result["zhi"]} → 藏干: {result["cang_gan"]} → 主气十神: {result["shi_shen"]}{mark}')
        if result['is_confused']:
            has_confusion = True
    
    if has_confusion:
        print('  ⚠️ 存在易混淆项，分析时务必查表确认！')
    else:
        print('  ✅ 无易混淆项')
    
    print('━━━━━━━━━━━━━━━━━━━━━━━━━━')

if __name__ == '__main__':
    main()
