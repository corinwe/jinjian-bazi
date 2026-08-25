#!/usr/bin/env python3
"""pipeline_v5 引擎输出 → bazi-data-source.py 兼容格式转换器
用法: python3 convert_v5_to_ds.py <engine.json> <output_ds.json>
"""
import json, sys, os

TIANGAN = "甲乙丙丁戊己庚辛壬癸"
DIZHI = "子丑寅卯辰巳午未申酉戌亥"
WX_MAP = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}

# 十神规则（以日主为基准）
SHISHEN_RULES = [
    ('比肩', lambda t, r: t == r),
    ('劫财', lambda t, r: WX_MAP[t] == WX_MAP[r] and t != r),
    ('食神', lambda t, r: WX_MAP[t] == _sheng(WX_MAP[r]) and _yinyang(t) == _yinyang(r)),
    ('伤官', lambda t, r: WX_MAP[t] == _sheng(WX_MAP[r]) and _yinyang(t) != _yinyang(r)),
    ('偏财', lambda t, r: WX_MAP[t] == _ke(WX_MAP[r]) and _yinyang(t) == _yinyang(r)),
    ('正财', lambda t, r: WX_MAP[t] == _ke(WX_MAP[r]) and _yinyang(t) != _yinyang(r)),
    ('七杀', lambda t, r: WX_MAP[r] == _ke(WX_MAP[t]) and _yinyang(t) == _yinyang(r)),
    ('正官', lambda t, r: WX_MAP[r] == _ke(WX_MAP[t]) and _yinyang(t) != _yinyang(r)),
    ('偏印', lambda t, r: WX_MAP[r] == _sheng(WX_MAP[t]) and _yinyang(t) == _yinyang(r)),
    ('正印', lambda t, r: WX_MAP[r] == _sheng(WX_MAP[t]) and _yinyang(t) != _yinyang(r)),
]

def _yinyang(g):
    return '阳' if TIANGAN.index(g) % 2 == 0 else '阴'

def _sheng(wx):
    return {'木':'火','火':'土','土':'金','金':'水','水':'木'}[wx]

def _ke(wx):
    return {'木':'土','土':'水','水':'火','火':'金','金':'木'}[wx]

def calc_shishen(tg, rizhu):
    for name, fn in SHISHEN_RULES:
        if fn(tg, rizhu):
            return name
    return '日主'

def get_xunkong(ganzhi):
    """日柱 → 空亡（旬空）
    正确算法：旬首地支 = (zi - gi) % 12，空亡 = (旬首+10)%12 和 (旬首+11)%12
    例：乙未 → 旬首午(6) → 辰巳 ✓
    """
    gi = TIANGAN.index(ganzhi[0])
    zi = DIZHI.index(ganzhi[1])
    xun_start = (zi - gi) % 12
    k1 = DIZHI[(xun_start + 10) % 12]
    k2 = DIZHI[(xun_start + 11) % 12]
    return k1 + k2

def calc_shensha(DS):
    """计算神煞（与 bazi-data-source.py 一致）"""
    rizhu, nz, rz, yz, sz = DS['日干'], DS['年支'], DS['日支'], DS['月支'], DS['时支']
    return {
        '天乙贵人': {'甲':'丑未','乙':'子申','丙':'酉亥','丁':'酉亥','戊':'丑未',
                    '己':'子申','庚':'丑未','辛':'午寅','壬':'巳卯','癸':'巳卯'}.get(rizhu, ''),
        '文昌贵人': {'甲':'巳','乙':'午','丙':'申','丁':'酉','戊':'申','己':'酉','庚':'亥','辛':'子','壬':'寅','癸':'卯'}.get(DS['年干'],''),
        '桃花': {'寅':'卯','卯':'子','辰':'酉','巳':'午','午':'卯','未':'子','申':'酉','酉':'午','戌':'卯','亥':'子','子':'酉','丑':'午'}.get(nz,''),
        '驿马': {'寅':'申','卯':'巳','辰':'寅','巳':'亥','午':'申','未':'巳','申':'寅','酉':'亥','戌':'申','亥':'巳','子':'寅','丑':'亥'}.get(nz,''),
        '华盖': {'寅':'戌','卯':'未','辰':'辰','巳':'丑','午':'戌','未':'未','申':'辰','酉':'丑','戌':'戌','亥':'未','子':'辰','丑':'丑'}.get(nz,''),
        '孤辰': {'亥':'寅','子':'寅','丑':'寅','寅':'巳','卯':'巳','辰':'巳',
                '巳':'申','午':'申','未':'申','申':'亥','酉':'亥','戌':'亥'}.get(nz,''),
        '寡宿': {'亥':'戌','子':'戌','丑':'戌','寅':'丑','卯':'丑','辰':'丑',
                '巳':'辰','午':'辰','未':'辰','申':'未','酉':'未','戌':'未'}.get(nz,''),
        '灾煞': {'申':'午','子':'午','辰':'午','寅':'子','午':'子','戌':'子',
                '巳':'卯','酉':'卯','丑':'卯','亥':'酉','卯':'酉','未':'酉'}.get(nz,''),
    }

def convert(engine_path, out_path):
    raw = json.load(open(engine_path))
    a = raw.get('analysis', {})
    basic = raw.get('basic_data', {})
    paipan = raw.get('paipan', {})

    # 四柱
    pillars = basic.get('pillars', {})
    sz = {
        '年柱': pillars['year']['gan'] + pillars['year']['zhi'],
        '月柱': pillars['month']['gan'] + pillars['month']['zhi'],
        '日柱': pillars['day']['gan'] + pillars['day']['zhi'],
        '时柱': pillars['hour']['gan'] + pillars['hour']['zhi'],
    }
    gs = ['年干','月干','日干','时干']
    zs = ['年支','月支','日支','时支']
    gz_list = [sz[k] for k in ['年柱','月柱','日柱','时柱']]

    DS = {}
    for k, g, z in zip(['年柱','月柱','日柱','时柱'], gs, zs):
        DS[g] = sz[k][0]
        DS[z] = sz[k][1]
    DS['8字段'] = [DS[k] for k in gs + zs]
    DS['四柱'] = sz
    DS['八字'] = ' '.join(gz_list)
    DS['日主'] = pillars['day']['gan']
    DS['日主五行'] = WX_MAP[DS['日主']]
    DS['性别'] = raw.get('gender', basic.get('gender', ''))

    # 藏干（从 basic_data pillars 提取）
    cang = {}
    for k in ['year','month','day','hour']:
        zhi = pillars[k]['zhi']
        cg = pillars[k].get('cang_gan', [])
        if not cg:
            cg = [zhi]  # 兜底
        items = []
        # 分配比例：本气100%，中气60%，余气30%
        ratios = ['100%','60%','30%']
        for i, c in enumerate(cg):
            items.append({'天干': c, '比例': ratios[i] if i < 3 else '30%'})
        cang[zhi + '支'] = items
    DS['藏干'] = cang
    DS['藏干十神'] = {k: [{'天干': c['天干'], '比例': c['比例'], '十神': calc_shishen(c['天干'], DS['日主'])} for c in v] for k, v in cang.items()}

    # 十神
    pos_key = {'年柱':'year','月柱':'month','日柱':'day','时柱':'hour'}
    shishen = {}
    for pos, g in zip(['年柱','月柱','日柱','时柱'], gs):
        ss = pillars[pos_key[pos]].get('shi_shen', '')
        if not ss:
            ss = '日主' if pos == '日柱' else calc_shishen(DS[g], DS['日主'])
        shishen[g] = ss
    DS['十神'] = shishen

    # 纳音
    DS['纳音'] = {k: pillars[k].get('na_yin', '') for k in ['year','month','day','hour']}
    DS['纳音'] = {k.replace('year','年柱').replace('month','月柱').replace('day','日柱').replace('hour','时柱'): v for k, v in DS['纳音'].items()}

    DS['空亡'] = get_xunkong(sz['日柱'])

    # 身强弱（从 analysis.shen_qiang_ruo）
    sqr = a.get('shen_qiang_ruo', {})
    score = sqr.get('score', 0)
    label = sqr.get('label', '')
    DS['身强弱'] = {'总分': score, '等级': label}

    # 大运
    dy = a.get('da_yun', {})
    dy_list = dy.get('list', []) if isinstance(dy, dict) else []
    if isinstance(dy, dict) and not dy_list:
        # 可能是 {list: [...]} 结构
        dy_list = dy.get('list', [])
    seq = []
    for i, d in enumerate(dy_list):
        seq.append({
            '序号': i + 1,
            '干支': d.get('gan','') + d.get('zhi','') if isinstance(d, dict) else str(d),
            '起始年龄': d.get('start_age', d.get('起始年龄', '')),
            '终止年龄': d.get('end_age', d.get('终止年龄', '')),
            '起始年份': d.get('start_year', d.get('起始年份', '')),
            '终止年份': d.get('end_year', d.get('终止年份', '')),
        })
    DS['大运'] = {
        '规则': '顺排' if '顺' in str(dy.get('direction','')) else '未知',
        '起运': str(dy.get('qi_yun_desc', dy.get('起运', ''))),
        '起运年龄': dy.get('qi_yun_age', dy.get('起运年龄', 0)),
        '序列': seq,
    }

    # 神煞
    DS['神煞'] = calc_shensha(DS)

    json.dump(DS, open(out_path, 'w'), ensure_ascii=False, indent=2)
    print(f"✅ {out_path} | {DS['八字']} | {DS['日主']}{DS['日主五行']} | 空亡:{DS['空亡']} | 大运:{len(seq)}步")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
