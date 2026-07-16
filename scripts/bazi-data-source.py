#!/usr/bin/env python3
"""
bazi-data-source.py ─ 八字数据源验证+锁定器 v2.1
老板指定架构：
  8字段(年干年支月干月支日干日支时干时支)+藏干+十神+纳音+空亡+神煞+起运年龄+十大运=唯一数据源
用法: python3 bazi-data-source.py /tmp/xxx_engine.json [/tmp/bazi_datasource.json]
"""

import json, os, sys

# ─── 全局常量 ───
TIANGAN = '甲乙丙丁戊己庚辛壬癸'
DIZHI = '子丑寅卯辰巳午未申酉戌亥'
WX_MAP = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
YY_MAP = {'甲':'阳','乙':'阴','丙':'阳','丁':'阴','戊':'阳','己':'阴','庚':'阳','辛':'阴','壬':'阳','癸':'阴'}
XUN_KONG = {'甲子':'戌亥','甲戌':'申酉','甲申':'午未','甲午':'辰巳','甲辰':'寅卯','甲寅':'子丑'}
XUN_MAP = {'甲':'甲子','乙':'甲戌','丙':'甲申','丁':'甲午','戊':'甲辰',
           '己':'甲子','庚':'甲戌','辛':'甲申','壬':'甲午','癸':'甲辰'}


def calc_shishen(tg, rizhu):
    """计算天干tg相对于日主rizhu的十神"""
    if tg == rizhu:
        return '日主'
    tg_wx = WX_MAP[tg]; rz_wx = WX_MAP[rizhu]
    tg_yy = YY_MAP[tg]; rz_yy = YY_MAP[rizhu]
    if tg_wx == rz_wx:
        return '比肩' if tg_yy == rz_yy else '劫财'
    sheng_wo = {'金':'土','木':'水','水':'金','火':'木','土':'火'}
    if sheng_wo.get(rz_wx) == tg_wx:
        return '偏印' if tg_yy != rz_yy else '正印'
    wo_sheng = {'金':'水','木':'火','水':'木','火':'土','土':'金'}
    if wo_sheng.get(rz_wx) == tg_wx:
        return '食神' if tg_yy == rz_yy else '伤官'
    ke_wo = {'金':'火','木':'金','水':'土','火':'水','土':'木'}
    if ke_wo.get(rz_wx) == tg_wx:
        return '七杀' if tg_yy != rz_yy else '正官'
    wo_ke = {'金':'木','木':'土','水':'火','火':'金','土':'水'}
    if wo_ke.get(rz_wx) == tg_wx:
        return '正财' if tg_yy != rz_yy else '偏财'
    return '?'


def get_xunkong(ganzhi):
    """计算日柱空亡"""
    return XUN_KONG.get(XUN_MAP.get(ganzhi[0], '甲子'), '')


def calc_shensha(DS):
    """计算神煞"""
    rizhu, nz, rz, yz, sz = DS['日干'], DS['年支'], DS['日支'], DS['月支'], DS['时支']
    return {
        '天乙贵人': {'甲':'丑未','乙':'子申','丙':'酉亥','丁':'酉亥','戊':'丑未',
                    '己':'子申','庚':'丑未','辛':'午寅','壬':'巳卯','癸':'巳卯'}.get(rizhu, ''),
        '文昌贵人': {'甲':'巳','乙':'午','丙':'申','丁':'酉','戊':'申','己':'酉','庚':'亥','辛':'子','壬':'寅','癸':'卯'}.get(rizhu,''),
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


def extend_dayun(dayun_list, nian_gan, gender, count=10):
    """扩展大运到count步。顺逆=年干阴阳+性别，非日干"""
    if len(dayun_list) >= count:
        return dayun_list[:count]
    last = dayun_list[-1]
    l_gan, l_zhi = last['干支'][0], last['干支'][1]
    l_age, l_year = last['终止年龄'], last['终止年份']
    is_shun = (YY_MAP[nian_gan] == '阳' and gender == '男') or (YY_MAP[nian_gan] == '阴' and gender == '女')
    gi = TIANGAN.index(l_gan)
    zi = DIZHI.index(l_zhi)
    extended = list(dayun_list)
    for i in range(len(dayun_list), count):
        gi = (gi + 1) % 10 if is_shun else (gi - 1) % 10
        zi = (zi + 1) % 12 if is_shun else (zi - 1) % 12
        l_age += 10; l_year += 10
        extended.append({'序号': i + 1, '干支': TIANGAN[gi] + DIZHI[zi],
                         '起始年龄': l_age - 9, '终止年龄': l_age,
                         '起始年份': l_year - 9, '终止年份': l_year})
    return extended


def load_and_validate(engine_path):
    """引擎JSON → 验证 → 补全 → 返回唯一数据源"""
    if not os.path.exists(engine_path):
        print(f"❌ 引擎缺失: {engine_path}"); return None
    raw = json.load(open(engine_path))

    DS = {}
    zk, gs, zs = ['年柱','月柱','日柱','时柱'], ['年干','月干','日干','时干'], ['年支','月支','日支','时支']
    for k, g, z in zip(zk, gs, zs):
        gz = raw['四柱'][k]; DS[g] = gz[0]; DS[z] = gz[1]
    DS['8字段'] = [DS[k] for k in gs + zs]
    DS['四柱'] = raw['四柱']
    DS['藏干'] = raw['藏干']
    rizhu = raw['日主']
    DS['藏干十神'] = {k: [{'天干':c['天干'],'比例':c['比例'],'十神':calc_shishen(c['天干'], rizhu)} for c in v] for k, v in raw['藏干'].items()}
    DS['十神'] = {k.replace('干',''): v for k, v in raw['十神'].items()}
    DS['纳音'] = raw['纳音']
    DS['空亡'] = get_xunkong(raw['四柱']['日柱'])
    DS['日主'] = rizhu
    DS['日主五行'] = raw['日主五行']
    DS['性别'] = raw['性别']
    DS['八字'] = raw['八字']
    DS['身强弱'] = raw['身强弱']
    DS['起运年龄'] = raw['大运']['起运']
    DS['起运年龄岁'] = raw['大运']['起运年龄']
    DS['神煞'] = calc_shensha(DS)
    DS['大运'] = extend_dayun(raw['大运']['序列'], DS['年干'], raw['性别'])
    
    required = ['年干','年支','月干','月支','日干','日支','时干','时支',
                '8字段','四柱','藏干','藏干十神','十神','纳音','空亡',
                '日主','日主五行','性别','八字','身强弱',
                '起运年龄','起运年龄岁','神煞','大运']
    missing = [r for r in required if r not in DS]
    if missing:
        print(f"❌ 数据源缺失: {missing}"); return None
    
    print(f"✅ 数据源通过 | {DS['八字']} | {rizhu}{DS['日主五行']} | 空亡:{DS['空亡']} | 神煞:{len(DS['神煞'])}种 | 大运:{len(DS['大运'])}步")
    return DS


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 bazi-data-source.py /tmp/xxx_engine.json [/tmp/bazi_datasource.json]")
        sys.exit(1)
    DS = load_and_validate(sys.argv[1])
    if DS:
        out = sys.argv[2] if len(sys.argv) > 2 else '/tmp/bazi_datasource.json'
        json.dump(DS, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f"✅ 已锁定: {out}")
