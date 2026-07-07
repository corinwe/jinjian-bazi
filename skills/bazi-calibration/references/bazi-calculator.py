"""
金鉴真人·八字排盘计算器（Python · 已校准）
基准已验证：2020-01-01 = 癸卯日 ✅ (日历网确认)
2026-06-04 校准
"""

import datetime

GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
ZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

# ===== 日柱基准 =====
# 2020-01-01 = 癸卯日 (gan=9, zhi=3)
KNOWN = datetime.date(2020, 1, 1)
BASE_GAN, BASE_ZHI = 9, 3

def day_pillar(y, m, d):
    t = datetime.date(y, m, d)
    delta = (t - KNOWN).days
    return GAN[(BASE_GAN + delta) % 10] + ZHI[(BASE_ZHI + delta) % 12]

# ===== 月柱（五虎遁）=====
# 节气表（年→[(月,日,地支名)]）
SOLAR_TERMS = {
    1980: [(1,6,'丑'),(2,5,'寅'),(3,5,'卯'),(4,4,'辰'),(5,5,'巳'),(6,5,'午'),
           (7,7,'未'),(8,7,'申'),(9,7,'酉'),(10,8,'戌'),(11,7,'亥'),(12,7,'子')],
    # 其他年份类似...
}

# 五虎遁：年干→正月天干索引
WUHU_START = {'甲':2,'己':2,'乙':4,'庚':4,'丙':6,'辛':6,'丁':8,'壬':8,'戊':0,'癸':0}

def get_month_zhi(y, m, d, terms):
    date_obj = datetime.date(y, m, d)
    result = '寅'
    for mm, dd, zhi in sorted(terms):
        if date_obj >= datetime.date(y, mm, dd):
            result = zhi
    return result

def month_pillar(y, m, d, year_gan, terms):
    mzhi = get_month_zhi(y, m, d, terms)
    # ⚠️ 关键修正：月份索引从寅=0开始
    zidx = (ZHI.index(mzhi) - 2) % 12
    gidx = (WUHU_START[year_gan] + zidx) % 10
    return GAN[gidx] + mzhi

# ===== 时柱（五鼠遁）=====
WUSHU_START = {'甲':0,'己':0,'乙':2,'庚':2,'丙':4,'辛':4,'丁':6,'壬':6,'戊':8,'癸':8}

def hour_pillar(day_gan, hour_zhi):
    """hour_zhi: 子=0,丑=1,寅=2,卯=3,辰=4,巳=5,午=6,未=7,申=8,酉=9,戌=10,亥=11"""
    gidx = (WUSHU_START[day_gan] + hour_zhi) % 10
    return GAN[gidx] + ZHI[hour_zhi]

# ===== 使用示例 =====
if __name__ == '__main__':
    # 家主：1980-08-06 卯时
    d = day_pillar(1980, 8, 6)
    m = month_pillar(1980, 8, 6, '庚', SOLAR_TERMS[1980])
    h = hour_pillar(d[0], 3)  # 卯=3
    print(f"家主: 庚申 {m} {d} {h}")
