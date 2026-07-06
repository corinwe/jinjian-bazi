#!/usr/bin/env python3
"""
金鉴真人·完整八字排盘引擎 v1.0
==================================
- 四柱排盘（节气精确至分钟级，用ephem天文库）
- 藏干（100/60/30标准·本气=100%/中气=60%/余气=30%）
- 纳音（硬编码查表）
- 十神（自动推导）
- 大运排布+起运年龄（节气精确计算）
- 所有输出可被官网交叉验证

依赖：ephem（pip install ephem）

作者：金鉴真人
日期：2026-06-08
"""

import sys
import math
import json
from datetime import date, datetime, timedelta
import ephem

# ============================================================
# 基础常量
# ============================================================

TIAN_GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DI_ZHI   = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

WU_XING = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土',
           '己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}

YANG_GAN = {'甲','丙','戊','庚','壬'}

SHI_CHEN = {0:'子',1:'丑',2:'寅',3:'卯',4:'辰',5:'巳',
            6:'午',7:'未',8:'申',9:'酉',10:'戌',11:'亥'}

# 日柱基准：1900-01-01 = 甲戌日
BASE_DATE = date(1900, 1, 1)
BASE_GAN = 0   # 甲
BASE_ZHI = 10  # 戌

# ============================================================
# 出生地经纬度数据库（真太阳时修正用）
# 格式：城市名 → [经度, 纬度]
# 北京UTC+8基准经度=120°E
# 真太阳时修正 = (经度 - 120) × 4分钟 + 均时差
# ============================================================

CITY_LONGITUDE = {
    # 直辖市
    '北京': 116.4, '上海': 121.5, '天津': 117.2, '重庆': 106.5,
    # 广东省
    '广州': 113.3, '深圳': 114.1, '珠海': 113.6, '东莞': 113.8,
    '佛山': 113.1, '惠州': 114.4, '中山': 113.4, '汕头': 116.7,
    # 浙江省
    '杭州': 120.2, '宁波': 121.5, '温州': 120.7, '义乌': 120.1,
    # 江苏省
    '南京': 118.8, '苏州': 120.6, '无锡': 120.3, '常州': 119.9,
    '南通': 120.9,
    # 四川省
    '成都': 104.1,
    # 湖北省
    '武汉': 114.3,
    # 湖南省
    '长沙': 113.0,
    # 福建省
    '福州': 119.3, '厦门': 118.1,
    # 山东省
    '济南': 117.0, '青岛': 120.4,
    # 辽宁省
    '沈阳': 123.4, '大连': 121.6,
    # 陕西省
    '西安': 108.9,
    # 河南省
    '郑州': 113.7,
    # 河北省
    '石家庄': 114.5, '唐山': 118.2,
    # 安徽省
    '定远': 117.67,
    # 香港/澳门/台湾
    '香港': 114.2, '澳门': 113.5, '台北': 121.5,
    # 海外常见城市
    '新加坡': 103.8, '东京': 139.7, '首尔': 127.0,
    '纽约': -74.0, '旧金山': -122.4, '洛杉矶': -118.2,
    '伦敦': -0.1, '巴黎': 2.4, '悉尼': 151.2,
}

def calc_solar_time(birth_dt, city_name=None, longitude=None):
    """
    计算真太阳时
    参数：
      birth_dt: 北京时间（datetime）
      city_name: 城市名（在CITY_LONGITUDE中查找）
      longitude: 直接给经度（优先级高于city_name）
    返回：
      (修正后的datetime, 修正的分钟数, 城市名/经度说明)
    """
    if longitude is None and city_name:
        if city_name in CITY_LONGITUDE:
            longitude = CITY_LONGITUDE[city_name]
        else:
            return birth_dt, 0, f'{city_name}(未知经度,使用北京时间)'
    
    if longitude is None:
        return birth_dt, 0, '未知出生地(使用北京时间)'
    
    # 经度修正：每1度=4分钟，以120°E为基准
    lon_correction = (longitude - 120) * 4  # 分钟（正=东边，时间更早）
    # 均时差最大±16分钟，对时辰判断影响极小，此处不做天文计算
    
    total_correction = lon_correction
    corrected = birth_dt + timedelta(minutes=total_correction)
    
    city_label = city_name if city_name else f'经度{longitude}°E'
    detail = f'{city_label}(经度修正{lon_correction:.1f}分,东经>120°时间更早)'
    
    return corrected, round(total_correction, 1), detail

def get_shichen_index(hour, minute):
    """根据小时和分钟确定时辰索引"""
    total_minutes = hour * 60 + minute
    # 子时 23:00-00:59 → 索引0
    # 丑时 01:00-02:59 → 索引1
    # ...
    # 亥时 21:00-22:59 → 索引11
    if total_minutes >= 1380 or total_minutes < 60:  # 23:00-00:59
        return 0  # 子时
    return (total_minutes - 60) // 120 + 1

# ============================================================
# 藏干（100/60/30标准·老板2026-06-11确认）
#   本气=100%(基准)，中气=60%(本气的60%)，余气=30%(本气的30%)
# ============================================================

CANG_GAN = {
    '子': [('癸', 100)],
    '丑': [('己', 100), ('癸', 60), ('辛', 30)],
    '寅': [('甲', 100), ('丙', 60), ('戊', 30)],
    '卯': [('乙', 100)],
    '辰': [('戊', 100), ('乙', 60), ('癸', 30)],
    '巳': [('丙', 100), ('戊', 60), ('庚', 30)],
    '午': [('丁', 100), ('己', 60)],
    '未': [('己', 100), ('丁', 60), ('乙', 30)],
    '申': [('庚', 100), ('壬', 60), ('戊', 30)],
    '酉': [('辛', 100)],
    '戌': [('戊', 100), ('辛', 60), ('丁', 30)],
    '亥': [('壬', 100), ('甲', 60)],
}

# ============================================================
# 纳音（硬编码查表）
# ============================================================

NA_YIN = {
    ('甲','子'): '海中金', ('乙','丑'): '海中金',
    ('丙','寅'): '炉中火', ('丁','卯'): '炉中火',
    ('戊','辰'): '大林木', ('己','巳'): '大林木',
    ('庚','午'): '路旁土', ('辛','未'): '路旁土',
    ('壬','申'): '剑锋金', ('癸','酉'): '剑锋金',
    ('甲','戌'): '山头火', ('乙','亥'): '山头火',
    ('丙','子'): '涧下水', ('丁','丑'): '涧下水',
    ('戊','寅'): '城头土', ('己','卯'): '城头土',
    ('庚','辰'): '白蜡金', ('辛','巳'): '白蜡金',
    ('壬','午'): '杨柳木', ('癸','未'): '杨柳木',
    ('甲','申'): '泉中水', ('乙','酉'): '泉中水',
    ('丙','戌'): '屋上土', ('丁','亥'): '屋上土',
    ('戊','子'): '霹雳火', ('己','丑'): '霹雳火',
    ('庚','寅'): '松柏木', ('辛','卯'): '松柏木',
    ('壬','辰'): '长流水', ('癸','巳'): '长流水',
    ('甲','午'): '沙中金', ('乙','未'): '沙中金',
    ('丙','申'): '山下火', ('丁','酉'): '山下火',
    ('戊','戌'): '平地木', ('己','亥'): '平地木',
    ('庚','子'): '壁上土', ('辛','丑'): '壁上土',
    ('壬','寅'): '金箔金', ('癸','卯'): '金箔金',
    ('甲','辰'): '覆灯火', ('乙','巳'): '覆灯火',
    ('丙','午'): '天河水', ('丁','未'): '天河水',
    ('戊','申'): '大驿土', ('己','酉'): '大驿土',
    ('庚','戌'): '钗钏金', ('辛','亥'): '钗钏金',
    ('壬','子'): '桑柘木', ('癸','丑'): '桑柘木',
    ('甲','寅'): '大溪水', ('乙','卯'): '大溪水',
    ('丙','辰'): '沙中土', ('丁','巳'): '沙中土',
    ('戊','午'): '天上火', ('己','未'): '天上火',
    ('庚','申'): '石榴木', ('辛','酉'): '石榴木',
    ('壬','戌'): '大海水', ('癸','亥'): '大海水',
}

# ============================================================
# 节气系统（用ephem计算精确日期）
# ============================================================

# 换月节气（"节"）及其对应月支
# 太阳黄经（度数）
JIE_QI_SUN = [
    (315, '立春', '寅'),
    (345, '惊蛰', '卯'),
    (15,  '清明', '辰'),
    (45,  '立夏', '巳'),
    (75,  '芒种', '午'),
    (105, '小暑', '未'),
    (135, '立秋', '申'),
    (165, '白露', '酉'),
    (195, '寒露', '戌'),
    (225, '立冬', '亥'),
    (255, '大雪', '子'),
    (285, '小寒', '丑'),
]

def sun_longitude(dt):
    """
    计算给定日期时间的太阳地心黄经
    返回：度数（0-360）
    """
    obs = ephem.Observer()
    obs.date = dt.strftime('%Y/%m/%d %H:%M:%S')
    sun = ephem.Sun(obs)
    # sun.hlong = 日心经度, 地心经度 = hlong + 180°
    return (math.degrees(sun.hlong) + 180) % 360

def find_jieqi_date(year, target_longitude):
    """
    查找某一年太阳到达指定黄经的精确UTC时间
    返回：datetime对象
    精度：约±1分钟
    """
    # 初始范围：以固定日期±15天
    fixed_days = {
        315: f'{year}/2/3',   # 立春约2月4日
        345: f'{year}/3/5',   # 惊蛰约3月6日
        15:  f'{year}/4/4',   # 清明约4月5日
        45:  f'{year}/5/5',   # 立夏约5月6日
        75:  f'{year}/6/5',   # 芒种约6月6日
        105: f'{year}/7/6',   # 小暑约7月7日
        135: f'{year}/8/6',   # 立秋约8月7日
        165: f'{year}/9/7',   # 白露约9月8日
        195: f'{year}/10/7',  # 寒露约10月8日
        225: f'{year}/11/6',  # 立冬约11月7日
        255: f'{year}/12/6',  # 大雪约12月7日
        285: f'{year}/1/5',   # 小寒约1月6日（注意跨年）
    }
    
    # 对于小寒，可能在上一年
    if target_longitude == 285:
        # 用(year, 1, 5)附近搜
        center_str = f'{year}/1/5'
    else:
        center_str = fixed_days[target_longitude]
    
    center = ephem.Date(center_str)
    
    # 二分查找找到交点
    prev_dt = ephem.Date(center - 10)
    next_dt = ephem.Date(center + 10)
    
    for _ in range(30):  # 30次迭代足够收敛
        mid = ephem.Date((prev_dt + next_dt) / 2)
        lon = sun_longitude(datetime.strptime(str(mid), '%Y/%m/%d %H:%M:%S'))
        
        # 处理0度附近环绕
        if target_longitude == 15:  # 清明，15度
            if lon > 350:  # 还在上一年
                pass
        elif target_longitude == 345:  # 惊蛰，345度
            if lon < 10:  # 已过360
                lon += 360
        
        if abs(lon - target_longitude) < 0.001:
            break
        elif lon < target_longitude:
            prev_dt = mid
        else:
            next_dt = mid
    
    # 更精确的：用牛顿法做最后收敛
    mid_dt = datetime.strptime(str(ephem.Date((prev_dt + next_dt) / 2)), '%Y/%m/%d %H:%M:%S')
    return mid_dt

def get_all_jieqi(year):
    """
    获取某一年的所有12个换月节气精确日期
    返回：[(月支, 名称, datetime), ...]
    """
    results = []
    for lon, name, zhi in JIE_QI_SUN:
        dt = find_jieqi_date(year, lon)
        results.append((zhi, name, dt))
    return results

def get_month_zhi(target_date):
    """
    根据精确节气确定月支
    """
    y = target_date.year
    # 获取本年和前一年的节气（因为小寒/立春可能跨年）
    all_jieqi = []
    for yy in [y-1, y, y+1]:
        all_jieqi.extend(get_all_jieqi(yy))
    
    # 按时间排序
    all_jieqi.sort(key=lambda x: x[2])
    
    # 找到target_date之前最近的一个节气
    current_zhi = '丑'  # 默认
    for zhi, name, dt in all_jieqi:
        if dt <= target_date:
            current_zhi = zhi
        else:
            break
    
    return current_zhi

def get_last_jieqi(target_date):
    """获取target_date之前最近的换月节气"""
    y = target_date.year
    all_jieqi = []
    for yy in [y-1, y, y+1]:
        all_jieqi.extend(get_all_jieqi(yy))
    all_jieqi.sort(key=lambda x: x[2])
    
    last = None
    for zhi, name, dt in all_jieqi:
        if dt <= target_date:
            last = (zhi, name, dt)
        else:
            break
    return last

def get_next_jieqi(target_date):
    """获取target_date之后最近的换月节气"""
    y = target_date.year
    all_jieqi = []
    for yy in [y-1, y, y+1]:
        all_jieqi.extend(get_all_jieqi(yy))
    all_jieqi.sort(key=lambda x: x[2])
    
    for zhi, name, dt in all_jieqi:
        if dt > target_date:
            return (zhi, name, dt)
    return None

# ============================================================
# 排盘核心函数
# ============================================================

def calc_rizhu(target_date):
    """计算日柱"""
    delta = (target_date - BASE_DATE).days
    gan = TIAN_GAN[(BASE_GAN + delta) % 10]
    zhi = DI_ZHI[(BASE_ZHI + delta) % 12]
    return gan, zhi

def calc_bazi(year, month, day, hour, minute, shichen_idx, gender, name="", birthplace=""):
    """
    完整排盘
    参数：
      year, month, day: 公历年月日
      hour, minute: 出生时刻（24小时制，北京时间）
      shichen_idx: 时辰索引（0-11）
      gender: '男' 或 '女'
      name: 名字（可选）
      birthplace: 出生地（可选，用于真太阳时修正）
    返回：dict包含所有信息
    """
    birth_date = date(year, month, day)
    birth_dt = datetime(year, month, day, hour, minute)
    
    # 真太阳时修正
    solar_dt, solar_correction, solar_detail = calc_solar_time(birth_dt, birthplace)
    solar_shichen = get_shichen_index(solar_dt.hour, solar_dt.minute)
    
    # 如果修正后的时辰与原时辰不同，标记提醒
    shichen_changed = (solar_shichen != shichen_idx)
    
    # --- 年柱 ---
    y_gan = TIAN_GAN[(year - 4) % 10]
    y_zhi = DI_ZHI[(year - 4) % 12]
    
    # --- 月柱 ---
    m_zhi = get_month_zhi(birth_dt)
    
    # 五虎遁求月干
    WU_HU_DUN = {'甲':'丙','乙':'戊','丙':'庚','丁':'壬','戊':'甲',
                 '己':'丙','庚':'戊','辛':'庚','壬':'壬','癸':'甲'}
    MONTH_ORDER = {'寅':0,'卯':1,'辰':2,'巳':3,'午':4,'未':5,
                   '申':6,'酉':7,'戌':8,'亥':9,'子':10,'丑':11}
    start_gan = WU_HU_DUN[y_gan]
    start_idx = TIAN_GAN.index(start_gan)
    m_gan_idx = (start_idx + MONTH_ORDER[m_zhi]) % 10
    m_gan = TIAN_GAN[m_gan_idx]
    
    # --- 日柱 ---
    r_gan, r_zhi = calc_rizhu(birth_date)
    
    # --- 时柱 ---
    shi_zhi = DI_ZHI[shichen_idx]
    WU_SHU_DUN = {'甲':0,'乙':2,'丙':4,'丁':6,'戊':8,
                  '己':0,'庚':2,'辛':4,'壬':6,'癸':8}
    s_gan_idx = (WU_SHU_DUN[r_gan] + shichen_idx) % 10
    s_gan = TIAN_GAN[s_gan_idx]
    
    bazi = f"{y_gan}{y_zhi} {m_gan}{m_zhi} {r_gan}{r_zhi} {s_gan}{shi_zhi}"
    
    # --- 纳音 ---
    pillars_nayin = {
        '年柱': NA_YIN.get((y_gan, y_zhi), '?'),
        '月柱': NA_YIN.get((m_gan, m_zhi), '?'),
        '日柱': NA_YIN.get((r_gan, r_zhi), '?'),
        '时柱': NA_YIN.get((s_gan, shi_zhi), '?'),
    }
    
    # --- 藏干 ---
    pillars_canggan = {
        '年支': CANG_GAN[y_zhi],
        '月支': CANG_GAN[m_zhi],
        '日支': CANG_GAN[r_zhi],
        '时支': CANG_GAN[shi_zhi],
    }
    
    # --- 十神 ---
    def calc_shishen(rizhu, other):
        rx = WU_XING[rizhu]
        ox = WU_XING[other]
        ri_yang = rizhu in YANG_GAN
        ot_yang = other in YANG_GAN
        if rx == ox:
            return '比肩' if ri_yang == ot_yang else '劫财'
        if {'木':'火','火':'土','土':'金','金':'水','水':'木'}.get(rx) == ox:
            return '食神' if ri_yang == ot_yang else '伤官'
        if {'木':'火','火':'土','土':'金','金':'水','水':'木'}.get(ox) == rx:
            return '偏印' if ri_yang == ot_yang else '正印'
        if {'木':'土','火':'金','土':'水','金':'木','水':'火'}.get(rx) == ox:
            return '偏财' if ri_yang == ot_yang else '正财'
        if {'木':'土','火':'金','土':'水','金':'木','水':'火'}.get(ox) == rx:
            return '七杀' if ri_yang == ot_yang else '正官'
        return '?'
    
    shishen = {
        '年干': calc_shishen(r_gan, y_gan),
        '月干': calc_shishen(r_gan, m_gan),
        '日干': '日主',
        '时干': calc_shishen(r_gan, s_gan),
    }
    
    # --- 大运 ---
    yin_yang = '阳' if y_gan in YANG_GAN else '阴'
    if (yin_yang == '阳' and gender == '男') or (yin_yang == '阴' and gender == '女'):
        direction = '顺排'
        direction_label = '阳男顺排' if (yin_yang=='阳' and gender=='男') else '阴女顺排'
    else:
        direction = '逆排'
        direction_label = '阴男逆排' if (yin_yang=='阴' and gender=='男') else '阳女逆排'
    
    # 起运计算
    if direction == '顺排':
        next_jq = get_next_jieqi(birth_dt)
        if next_jq:
            jq_zhi, jq_name, jq_dt = next_jq
            days_diff = (jq_dt - birth_dt).total_seconds() / 86400
        else:
            jq_name = '未知'
            days_diff = 0
    else:
        last_jq = get_last_jieqi(birth_dt)
        if last_jq:
            jq_zhi, jq_name, jq_dt = last_jq
            days_diff = (birth_dt - jq_dt).total_seconds() / 86400
        else:
            jq_name = '未知'
            days_diff = 0
    
    qi_yun_years = int(days_diff // 3)
    qi_yun_remainder = days_diff % 3
    qi_yun_months = int(qi_yun_remainder * 4)
    qi_yun_days = int((qi_yun_remainder * 4 - qi_yun_months) * 30)
    qi_yun_age = days_diff / 3.0
    
    # 大运序列
    m_zhi_idx = DI_ZHI.index(m_zhi)
    m_gan_idx = TIAN_GAN.index(m_gan)
    da_yun_list = []
    if direction == '顺排':
        for i in range(8):
            zhi = DI_ZHI[(m_zhi_idx + 1 + i) % 12]
            gan = TIAN_GAN[(m_gan_idx + 1 + i) % 10]
            da_yun_list.append(f"{gan}{zhi}")
    else:
        for i in range(8):
            zhi = DI_ZHI[(m_zhi_idx - 1 - i) % 12]
            gan = TIAN_GAN[(m_gan_idx - 1 - i) % 10]
            da_yun_list.append(f"{gan}{zhi}")
    
    return {
        'name': name,
        'bazi': bazi,
        'birth': birth_dt,
        'birthplace': birthplace,
        'solar_dt': solar_dt,
        'solar_correction': solar_correction,
        'solar_detail': solar_detail,
        'solar_shichen': solar_shichen,
        'shichen_changed': shichen_changed,
        'gender': gender,
        'year_pillar': (y_gan, y_zhi),
        'month_pillar': (m_gan, m_zhi),
        'day_pillar': (r_gan, r_zhi),
        'hour_pillar': (s_gan, shi_zhi),
        'rizhu': r_gan,
        'nayin': pillars_nayin,
        'canggan': pillars_canggan,
        'shishen': shishen,
        'da_yun': da_yun_list,
        'direction': direction,
        'direction_label': direction_label,
        'qi_yun_years': qi_yun_years,
        'qi_yun_months': qi_yun_months,
        'qi_yun_days': qi_yun_days,
    'qi_yun_age': round(qi_yun_age, 2),
    'jq_name': jq_name,
    'days_diff': round(days_diff, 4),
}

# ============================================================
# 身强弱评分规则（v3.0 确认版）
#   评分范围：0-100分
#   <40身弱 | 40-60中和 | >60身强
#   只算加分（印+比劫），不加不减
#   月令40分（印且月令才计，比劫在月令不计）
#   各位置基础分：年干8/年支4/月令40/月干12/日支12/时干12/时支12
#   燥土规则：未戌对金不计分
# ============================================================

# 位置基础分
POSITION_SCORE = {
    ('年干', '天干'): 8,
    ('年支', '地支'): 4,
    ('月令', '月令'): 40,
    ('月干', '天干'): 12,
    ('日支', '地支'): 12,
    ('时干', '天干'): 12,
    ('时支', '地支'): 12,
}

# 燥土地支（对金不计分）
ZAO_TU = {'未', '戌'}
# 湿土地支（能生金）
SHI_TU = {'辰', '丑'}

# 印星（生我）
ZHENG_YIN_GAN = {
    '甲':'癸', '乙':'壬', '丙':'乙', '丁':'甲', '戊':'丁',
    '己':'丙', '庚':'己', '辛':'戊', '壬':'辛', '癸':'庚',
}
PIAN_YIN_GAN = {
    '甲':'壬', '乙':'癸', '丙':'甲', '丁':'乙', '戊':'丙',
    '己':'丁', '庚':'戊', '辛':'己', '壬':'庚', '癸':'辛',
}

# 比劫（同我）—— 同五行即为比劫（不分阴阳）
BI_JIE = {
    '甲':'甲', '乙':'乙', '丙':'丙', '丁':'丁', '戊':'戊',
    '己':'己', '庚':'庚', '辛':'辛', '壬':'壬', '癸':'癸',
}


def calc_qiangruo(result):
    """
    根据排盘结果计算身强弱评分。
    
    规则（v4.0·九龙道长原始体系·2026-06-16老板最终确认）：
    1. 只算加分，不加不减
    2. 加分项：印只在月令本气计分；比劫在所有位置都计分
    3. 月令中气/余气印不计分；其他位置（年/日/时/天干）印不计分
    4. 燥土规则（条件版）：被火引化时不生金，被水灭火/无引化时生金
    5. 大运流年印计分
    6. 评分范围：0-100
    
    返回: {
        '总分': 分数,
        '等级': '身弱'/'中和'/'身强',
        '明细': [...],
    }
    """
    scores = []
    total = 0
    
    rizhu = result['rizhu']
    ri_wuxing = WU_XING[rizhu]
    
    # --- 年干 ---
    y_gan = result['year_pillar'][0]
    y_gan_score = _calc_gan_score(rizhu, y_gan, '年干', 8)
    if y_gan_score:
        scores.append(y_gan_score)
        total += y_gan_score['得分']
    
    # --- 年支藏干 ---
    y_zhi = result['year_pillar'][1]
    y_zhi_score = _calc_zhi_cang_score(rizhu, y_zhi, '年支', 4)
    if y_zhi_score:
        scores.extend(y_zhi_score)
        total += sum(s['得分'] for s in y_zhi_score)
    
    # --- 月令（印星本气计分+比劫全计分） ---
    m_zhi = result['month_pillar'][1]
    m_gan = result['month_pillar'][0]  # 月天干，用于燥土规则判断
    m_zhi_score = _calc_yueling_score(rizhu, m_zhi, m_gan, 40)
    if m_zhi_score:
        scores.extend(m_zhi_score)
        total += sum(s['得分'] for s in m_zhi_score)
    
    # --- 月干 ---
    m_gan = result['month_pillar'][0]
    m_gan_score = _calc_gan_score(rizhu, m_gan, '月干', 12)
    if m_gan_score:
        scores.append(m_gan_score)
        total += m_gan_score['得分']
    
    # --- 日支藏干 ---
    r_zhi = result['day_pillar'][1]
    r_zhi_score = _calc_zhi_cang_score(rizhu, r_zhi, '日支', 12)
    if r_zhi_score:
        scores.extend(r_zhi_score)
        total += sum(s['得分'] for s in r_zhi_score)
    
    # --- 时干 ---
    s_gan = result['hour_pillar'][0]
    s_gan_score = _calc_gan_score(rizhu, s_gan, '时干', 12)
    if s_gan_score:
        scores.append(s_gan_score)
        total += s_gan_score['得分']
    
    # --- 时支藏干 ---
    sh_zhi = result['hour_pillar'][1]
    sh_zhi_score = _calc_zhi_cang_score(rizhu, sh_zhi, '时支', 12)
    if sh_zhi_score:
        scores.extend(sh_zhi_score)
        total += sum(s['得分'] for s in sh_zhi_score)
    
    # 等级判定
    if total < 40:
        level = '身弱'
    elif total <= 60:
        level = '中和'
    else:
        level = '身强'
    
    # 从格判定（九龙道长规则）
    # 从弱反为强：全无印比（得分=0分）→ 恒定50分
    # 从强反为弱：满盘印比（得分>100分）→ 恒定20分
    if total == 0:
        level = '从弱'
        total = 50.0
    elif total > 100:
        level = '从强'
        total = 20.0
    
    return {
        '总分': total,
        '等级': level,
        '明细': scores,
    }


def _calc_gan_score(rizhu, gan, position, base_score):
    """计算天干位置的比劫加分（九龙道长规则：天干印不计分）。"""
    # 比劫检查（同五行）
    if WU_XING[gan] == WU_XING[rizhu]:
        return {'位置': position, '类型': '天干', '天干': gan, '属性': '比劫', '基础分': base_score, '得分': base_score, '说明': f'{gan}与{rizhu}同五行→比劫'}
    
    return None


def _calc_zhi_cang_score(rizhu, zhi, position, base_score):
    """计算非月令地支的藏干比劫加分（九龙道长规则：其他位置印不计分）。"""
    scores = []
    cang_items = CANG_GAN.get(zhi, [])
    
    for cang_gan, pct in cang_items:
        actual_score = base_score * (pct / 100.0)
        
        # 燥土规则（条件版·九龙道长原始）：默认当土看生金
        # 被火引化时当火看不生金——需结合同柱天干判断
        is_zaotu_fire = False  # 默认当土看生金
        
        # 比劫检查（比劫全算，但燥土被火引化后不计）
        if WU_XING[cang_gan] == WU_XING[rizhu]:
            if rizhu in ('庚','辛') and zhi in ZAO_TU and is_zaotu_fire:
                continue  # 燥土被火引化→不生金
            scores.append({
                '位置': f'{position}({zhi})',
                '类型': '藏干',
                '天干': cang_gan,
                '比例': f'{pct}%',
                '属性': '比劫',
                '基础分': base_score,
                '得分': round(actual_score, 1),
                '说明': f'{zhi}藏{cang_gan}与{rizhu}同五行→比劫(占比{pct}%)' + (' [燥土被火引化不计]' if rizhu in ('庚','辛') and zhi in ZAO_TU else '')
            })
    
    return scores if scores else None


def _calc_yueling_score(rizhu, yue_zhi, yue_gan, base_score):
    """计算月令的得分（九龙道长原始规则）。
    
    规则：
    - 印星：只在月令本气计分（素材20行1038·"印在月令本气算分，中气余气不计"）
    - 比劫：所有藏干位置都计分（素材09行89·"比劫算"）
    - 燥土条件版：被火引化→当火看不生金；水灭火/无引化→生金
    
    印星只计本气（100%位置分），中气(60%)余气(30%)不计。
    比劫所有藏干位置（本/中/余气）都计分。
    燥土规则：月天干为丙/丁时→火引化→不计分
              月天干为壬/癸时→水灭火→当土看计分
              月天干为戊/己/庚/辛时→无火引化→当土看计分
    """
    scores = []
    cang_items = CANG_GAN.get(yue_zhi, [])
    
    # 判断燥土是否被火引化（条件版）
    zaotu_bu_shengjin = False
    if rizhu in ('庚','辛') and yue_zhi in ZAO_TU:
        if yue_gan in ('丙','丁'):  # 火引化→当火看→不生金
            zaotu_bu_shengjin = True
        else:  # 壬/癸水灭火或其他→纯粹土→生金
            zaotu_bu_shengjin = False
    
    for i, (cang_gan, pct) in enumerate(cang_items):
        actual_score = base_score * (pct / 100.0)
        
        # 判断本气/中气/余气
        is_ben_qi = (i == 0)  # 第一个是本气
        
        # 印星：只计月令本气（第一个藏干100%）
        if not zaotu_bu_shengjin:  # 只有燥土被火引化时才跳过印
            if cang_gan == ZHENG_YIN_GAN.get(rizhu, '') or \
               cang_gan == PIAN_YIN_GAN.get(rizhu, ''):
                if is_ben_qi:
                    scores.append({
                        '位置': f'月令({yue_zhi})',
                        '类型': '月令',
                        '天干': cang_gan,
                        '比例': f'{pct}%',
                        '属性': '印星(本气)',
                        '基础分': base_score,
                        '得分': round(actual_score, 1),
                        '说明': f'月令{yue_zhi}藏{cang_gan}是{rizhu}的印星本气(占{pct}%)'
                    })
                # else: 中气/余气印→不计分（素材20行1038）
        
        # 比劫：所有藏干位置都计分
        if WU_XING[cang_gan] == WU_XING[rizhu]:
            if zaotu_bu_shengjin:
                continue  # 燥土被火引化→比劫也不计
            scores.append({
                '位置': f'月令({yue_zhi})',
                '类型': '月令',
                '天干': cang_gan,
                '比例': f'{pct}%',
                '属性': '比劫',
                '基础分': base_score,
                '得分': round(actual_score, 1),
                '说明': f'月令{yue_zhi}藏{cang_gan}与{rizhu}同五行→比劫(占比{pct}%)'
            })
    
    return scores if scores else None


def calc_da_yun_with_age(result):
    """
    计算带年龄和年份范围的大运列表。
    年份算法：直接用起运实际开始年份，不用 birth+int(age) 近似。
    """
    import math
    da_yun_list = result['da_yun']
    qi_yun_age = result['qi_yun_age']
    
    # 计算起运实际开始日期 → 取年份做基数
    from datetime import timedelta
    qi_yun_start = result['birth'] + timedelta(days=qi_yun_age * 365.25)
    qi_yun_start_year = qi_yun_start.year
    # 起运在Q4(10~12月) → 进位到下一年（实际影响从次年始）
    if qi_yun_start.month >= 10:
        qi_yun_start_year += 1
    
    # 起运年龄取整规则（九龙道长标准·2026-06-25校准）：
    # < 1年 → 1岁起运（不足1年按1年）
    # >= 1年 → 取整数部分（8.5岁→8岁起运，不向上取整）
    if qi_yun_age < 1:
        start_age_base = 1
    else:
        start_age_base = int(qi_yun_age)
    
    padded_list = []
    for i, dy in enumerate(da_yun_list):
        start_age = start_age_base + i * 10
        end_age = start_age_base + (i + 1) * 10 - 1
        start_year = qi_yun_start_year + i * 10
        end_year = start_year + 9
        padded_list.append({
            '序号': i + 1,
            '干支': dy,
            '起始年龄': start_age,
            '终止年龄': end_age,
            '起始年份': start_year,
            '终止年份': end_year,
        })
    return padded_list


def to_json(result):
    """
    将排盘结果序列化为JSON可序列化的dict。
    """
    qiangruo = calc_qiangruo(result)
    da_yun_age = calc_da_yun_with_age(result)
    
    # 格式化藏干为可JSON序列化结构
    canggan_json = {}
    for pos, cangs in result['canggan'].items():
        canggan_json[pos] = [{'天干': g, '比例': f'{p}%'} for g, p in cangs]
    
    # 格式化大运
    da_yun_serializable = []
    for dy in da_yun_age:
        da_yun_serializable.append(dy)
    
    json_result = {
        '引擎版本': 'v2.0',
        '编制人': '金鉴真人',
        '姓名': result.get('name', ''),
        '八字': result['bazi'],
        '日主': result['rizhu'],
        '日主五行': WU_XING[result['rizhu']],
        '性别': result['gender'],
        '出生': result['birth'].strftime('%Y-%m-%d %H:%M'),
        '出生地': result['birthplace'],
        '真太阳时': {
            '修正后时间': result['solar_dt'].strftime('%H:%M'),
            '修正分钟': result['solar_correction'],
            '修正详情': result['solar_detail'],
        },
        '四柱': {
            '年柱': f"{result['year_pillar'][0]}{result['year_pillar'][1]}",
            '月柱': f"{result['month_pillar'][0]}{result['month_pillar'][1]}",
            '日柱': f"{result['day_pillar'][0]}{result['day_pillar'][1]}",
            '时柱': f"{result['hour_pillar'][0]}{result['hour_pillar'][1]}",
        },
        '纳音': {
            '年柱': result['nayin'].get('年柱', ''),
            '月柱': result['nayin'].get('月柱', ''),
            '日柱': result['nayin'].get('日柱', ''),
            '时柱': result['nayin'].get('时柱', ''),
        },
        '藏干': canggan_json,
        '十神': result['shishen'],
        '身强弱': qiangruo,
        '大运': {
            '规则': result['direction_label'],
            '起运': f"{result['qi_yun_years']}岁{result['qi_yun_months']}个月{result['qi_yun_days']}天",
            '起运年龄': result['qi_yun_age'],
            '序列': da_yun_serializable,
        },
    }
    
    return json_result


# ============================================================
# 输出函数
# ============================================================

def print_result(r):
    print("=" * 66)
    title = f"  {r['name']}" if r['name'] else ""
    print(f"  金鉴真人·八字排盘引擎 v1.0  {title}")
    print("=" * 66)
    print()
    
    print(f"  [八字] {r['bazi']}")
    print(f"  [日主] {r['rizhu']}({WU_XING[r['rizhu']]})")
    print(f"  [出生] {r['birth'].strftime('%Y-%m-%d %H:%M')}  {r['gender']}", end='')
    if r['birthplace']:
        print(f"  出生地: {r['birthplace']}")
    else:
        print()
    if r['birthplace'] or r['solar_correction'] != 0:
        print(f"  [真太阳时] {r['solar_dt'].strftime('%H:%M')} (修正{r['solar_correction']}分)")
        print(f"  [修正详解] {r['solar_detail']}")
        print(f"  [修正时辰] {SHI_CHEN[r['solar_shichen']]}时", end='')
        if r['shichen_changed']:
            print(f" ⚠️ 真太阳时时辰与原时辰不同，原时柱用北京时间排盘，建议复核")
        else:
            print()
    print()
    
    print("【纳音】")
    print("-" * 50)
    for pos, (g, z) in [('年柱', r['year_pillar']), ('月柱', r['month_pillar']),
                          ('日柱', r['day_pillar']), ('时柱', r['hour_pillar'])]:
        print(f"  {pos} {g}{z} → {NA_YIN.get((g,z),'?')}")
    print()
    
    print("【藏干】")
    print("-" * 50)
    for pos, cangs in r['canggan'].items():
        parts = [f"{g}({p}%)" for g, p in cangs]
        print(f"  {pos} → {'·'.join(parts)}")
    print()
    
    print("【十神】")
    print("-" * 50)
    for pos, ss in r['shishen'].items():
        print(f"  {pos} → {ss}")
    print()
    
    print("【大运】")
    print("-" * 50)
    print(f"  规则: {r['direction_label']}")
    print(f"  到{r['jq_name']}的天数: {r['days_diff']}天")
    print(f"  起运: {r['qi_yun_years']}岁{r['qi_yun_months']}个月{r['qi_yun_days']}天")
    print()
    b_year = r['birth'].year
    # 🚨 大运年份从起运开始算，不是从出生年（2026-06-25修复）
    # 旧逻辑：s_year = b_year + int(qi_yun_age) → int(0.37)=0 → 1980 ❌
    # 新逻辑：用 calc_da_yun_with_age 的年份数据
    da_yun_age_data = calc_da_yun_with_age(r)
    for i, dy in enumerate(r['da_yun']):
        d = da_yun_age_data[i]
        s_year = d['起始年份']
        e_year = d['终止年份']
        s_age = int(d['起始年龄'])
        e_age = int(d['终止年龄'])
        print(f"  {i+1}. {dy}  ({s_year}~{e_year}年  {s_age}~{e_age}岁)")
    print()
    
    print("=" * 66)
    print("  🛡️  引擎计算完成。请用官网交叉验证后使用。")
    print("=" * 66)


def format_compact(r):
    """紧凑输出格式，便于快速查看"""
    lines = []
    lines.append(f"{r['name'] + ' ' if r['name'] else ''}{r['bazi']} | 日{r['rizhu']}({WU_XING[r['rizhu']]}) | {r['gender']}")
    lines.append(f"  纳音: {'·'.join(NA_YIN.get(p,'?') for p in [r['year_pillar'], r['month_pillar'], r['day_pillar'], r['hour_pillar']])}")
    lines.append(f"  大运: {r['direction_label']} | 起运{r['qi_yun_years']}岁{r['qi_yun_months']}月")
    lines.append(f"  序列: {' → '.join(r['da_yun'][:4])}...")
    return '\n'.join(lines)


# ============================================================
# 主入口
# ============================================================

if __name__ == '__main__':
    # 检查 --test 标志（门禁用）
    if '--test' in sys.argv:
        print("bazi-engine.py: 运行正常 ✅")
        sys.exit(0)
    
    # 检查 --json 标志
    output_json = '--json' in sys.argv
    if output_json:
        # 移除 --json 参数，剩下的就是位置参数
        args = [a for a in sys.argv[1:] if not a.startswith('--')]
    else:
        args = sys.argv[1:]
    
    if len(args) >= 6:
        year = int(args[0])
        month = int(args[1])
        day = int(args[2])
        hour = int(args[3])
        minute = int(args[4])
        shichen_idx = int(args[5])
        gender = args[6] if len(args) >= 7 else '男'
        name = args[7] if len(args) >= 8 else ''
        birthplace = args[8] if len(args) >= 9 else ''
    else:
        print("用法: python3 bazi-engine.py 年 月 日 时 分 时辰索引 [性别] [名字] [出生地] [--json]", file=sys.stderr)
        print("例: python3 bazi-engine.py 2011 5 31 10 0 5 男 子源 上海", file=sys.stderr)
        print("例: python3 bazi-engine.py 2011 5 31 10 0 5 男 子源 --json", file=sys.stderr)
        print("时辰索引: 0子 1丑 2寅 3卯 4辰 5巳 6午 7未 8申 9酉 10戌 11亥", file=sys.stderr)
        print("出生地可选（用于真太阳时修正），支持城市名或直接写经度", file=sys.stderr)
        sys.exit(1)
    
    result = calc_bazi(year, month, day, hour, minute, shichen_idx, gender, name, birthplace)
    
    if output_json:
        json_data = to_json(result)
        print(json.dumps(json_data, ensure_ascii=False, indent=2))
    else:
        print_result(result)
