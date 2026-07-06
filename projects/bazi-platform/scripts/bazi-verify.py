#!/usr/bin/env python3
"""
金鉴真人·八字排盘物理验证系统 v1.0
=================================
不依赖记忆，不依赖感觉，代码硬算才是最准的。
每次排八字前强制运行此脚本。

用法：python3 bazi-verify.py [年] [月] [日] [时辰索引0-11] [性别男/女]
      或直接运行进入交互模式

时辰索引：子0 丑1 寅2 卯3 辰4 巳5 午6 未7 申8 酉9 戌10 亥11
"""

import sys
from datetime import date
from nayin import get_na_yin, NA_YIN

# ============================================================
# 一、基础常量（硬编码，不依赖任何外部数据）
# ============================================================

TIAN_GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DI_ZHI   = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

# 基准：1900-01-01 = 甲戌日（多个锚点验证过的正确基准）
BASE_DATE = date(1900, 1, 1)
BASE_GAN = 0   # 甲
BASE_ZHI = 10  # 戌

# ============================================================
# 二、藏干表（100/60/30标准·金鉴真人原始规则）
# 规则：本气=100%·中气=60%·余气=30%
# 巳的规则：丙火(本100)→戊土(中60,火生土)→庚金(余30,土生金)
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
# 三、五虎遁（年干→正月干）
# ============================================================

WU_HU_DUN = {
    '甲':'丙', '乙':'戊', '丙':'庚', '丁':'壬', '戊':'甲',
    '己':'丙', '庚':'戊', '辛':'庚', '壬':'壬', '癸':'甲'
}

# ============================================================
# 四、五鼠遁（日干→子时干的天干索引偏移）
# ============================================================

WU_SHU_DUN = {
    '甲':0, '乙':2, '丙':4, '丁':6, '戊':8,
    '己':0, '庚':2, '辛':4, '壬':6, '癸':8
}
# 0=甲, 2=丙, 4=戊, 6=庚, 8=壬

# ============================================================
# 五、验证锚点（经实际排盘工具验证的已知正确日柱）
# ============================================================

ANCHORS = {
    date(1987, 7, 20): ('庚','午'),   # 主母旧日期验证
    date(1987, 7, 31): ('辛','巳'),   # 主母正确日期验证
    date(2011, 5, 31): ('丙','戌'),   # 子源（用户确认）
    date(2011, 5, 19): ('甲','戌'),   # 立（用户确认）
    date(1949, 10, 1): ('甲','子'),   # 新中国成立（万年历确认）
}

# ============================================================
# 六、节气表（月柱节气划分 + 换月节气起运计算）
# ============================================================

JIE_QI = {  # 每月节气日（阳历）
    1: 6,   # 小寒
    2: 4,   # 立春
    3: 6,   # 惊蛰
    4: 5,   # 清明
    5: 6,   # 立夏
    6: 6,   # 芒种
    7: 7,   # 小暑
    8: 7,   # 立秋
    9: 8,   # 白露
    10: 8,  # 寒露
    11: 7,  # 立冬
    12: 7,  # 大雪
}

# 换月节气（"节"，用于大运起运计算）
# 格式：(月份, 日期, 名称, 对应的月支)
# 每年±1天波动，此表为近似值
HUAN_YUE_JIE = [
    (1, 6, '小寒', '丑'),
    (2, 4, '立春', '寅'),
    (3, 6, '惊蛰', '卯'),
    (4, 5, '清明', '辰'),
    (5, 6, '立夏', '巳'),
    (6, 6, '芒种', '午'),
    (7, 7, '小暑', '未'),
    (8, 7, '立秋', '申'),
    (9, 8, '白露', '酉'),
    (10, 8, '寒露', '戌'),
    (11, 7, '立冬', '亥'),
    (12, 7, '大雪', '子'),
]

MONTH_ZHI_MAP = {1:'丑',2:'寅',3:'卯',4:'辰',5:'巳',6:'午',
                 7:'未',8:'申',9:'酉',10:'戌',11:'亥',12:'子'}

# 月支的顺序
MONTH_ORDER = {'寅':0,'卯':1,'辰':2,'巳':3,'午':4,'未':5,
               '申':6,'酉':7,'戌':8,'亥':9,'子':10,'丑':11}

# ============================================================
# 七、五行
# ============================================================

WU_XING = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土',
           '己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}

YANG_GAN = {'甲','丙','戊','庚','壬'}

# ============================================================
# 八、核心函数
# ============================================================

def calc_rizhu(target_date):
    """计算日柱干支，用代码硬算"""
    delta = (target_date - BASE_DATE).days
    gan = TIAN_GAN[(BASE_GAN + delta) % 10]
    zhi = DI_ZHI[(BASE_ZHI + delta) % 12]
    return gan, zhi


def verify_anchors():
    """验证基准日是否正确——这是脚本自检"""
    print("=" * 66)
    print("  八字排盘物理验证系统 v1.0")
    print("  金鉴真人体系 | 2026-06-08")
    print("=" * 66)
    print()
    print("【基准日自检】1900-01-01 = 甲戌日")
    print()

    all_pass = True
    for dt, expected in sorted(ANCHORS.items()):
        gan, zhi = calc_rizhu(dt)
        status = "✅" if (gan, zhi) == expected else "❌"
        if (gan, zhi) != expected:
            all_pass = False
            print(f"  {status} {dt} → 算出 {gan}{zhi}，期望 {expected[0]}{expected[1]} ← 错误！")
        else:
            print(f"  {status} {dt} = {gan}{zhi}")

    if not all_pass:
        print("\n⚠️ 锚点验证失败！基准日计算有误，不可用此脚本排盘！")
        sys.exit(1)
    else:
        print("\n✅ 所有锚点验证通过，基准日正确。")
    print()


def calc_bazi(year, month, day, shichen_idx, gender):
    """计算完整八字"""
    target = date(year, month, day)
    
    # --- 年柱 ---
    y_gan = TIAN_GAN[(year - 4) % 10]
    y_zhi = DI_ZHI[(year - 4) % 12]
    
    # --- 月柱 ---
    # 先确定月支（按节气）
    m_zhi = MONTH_ZHI_MAP[month]
    if day < JIE_QI.get(month, 1) and month != 1:
        prev = month - 1
        if prev == 0:
            prev = 12
        m_zhi = MONTH_ZHI_MAP[prev]
    
    # 月干（五虎遁）
    start_gan = WU_HU_DUN[y_gan]
    start_idx = TIAN_GAN.index(start_gan)
    m_gan_idx = (start_idx + MONTH_ORDER[m_zhi]) % 10
    m_gan = TIAN_GAN[m_gan_idx]
    
    # --- 日柱 ---
    r_gan, r_zhi = calc_rizhu(target)
    
    # --- 时柱 ---
    shi_zhi = DI_ZHI[shichen_idx]
    s_gan_idx = (WU_SHU_DUN[r_gan] + shichen_idx) % 10
    s_gan = TIAN_GAN[s_gan_idx]
    
    bazi = f"{y_gan}{y_zhi} {m_gan}{m_zhi} {r_gan}{r_zhi} {s_gan}{shi_zhi}"
    
    return {
        'bazi': bazi,
        'year': (y_gan, y_zhi),
        'month': (m_gan, m_zhi),
        'day': (r_gan, r_zhi),
        'hour': (s_gan, shi_zhi),
        'rizhu': r_gan,
        'ri_zhi': r_zhi,
    }


def print_cang_gan(result):
    """打印所有地支的藏干（逐字标注）"""
    print("【地支逐字标注】")
    print("-" * 50)
    
    positions = [
        ('年支', result['year'][1]),
        ('月支', result['month'][1]),
        ('日支', result['day'][1]),
        ('时支', result['hour'][1]),
    ]
    
    for pos_name, zhi in positions:
        cangs = CANG_GAN[zhi]
        parts = [f"{g}({p}%)" for g, p in cangs]
        print(f"  {pos_name}={zhi} → {'·'.join(parts)}")
    
    print()
    # 高亮特别提醒
    for pos_name, zhi in positions:
        if zhi == '巳':
            print(f"  ⚠️ {pos_name}巳：庚金=余气30%（火→土→金递降）")
        if zhi == '戌':
            print(f"  ⚠️ {pos_name}戌：辛金=中气60%")
    print()


def get_shishen(rizhu, other_stem):
    """计算某个字对日主的十神"""
    rx = WU_XING[rizhu]
    ox = WU_XING[other_stem]
    ri_yang = rizhu in YANG_GAN
    ot_yang = other_stem in YANG_GAN
    
    # 同我
    if rx == ox:
        return '比肩' if ri_yang == ot_yang else '劫财'
    
    # 我生
    if (rx, ox) in [('木','火'),('火','土'),('土','金'),('金','水'),('水','木')]:
        return '食神' if ri_yang == ot_yang else '伤官'
    
    # 生我
    if (ox, rx) in [('木','火'),('火','土'),('土','金'),('金','水'),('水','木')]:
        return '偏印' if ri_yang == ot_yang else '正印'
    
    # 我克
    if (rx, ox) in [('木','土'),('火','金'),('土','水'),('金','木'),('水','火')]:
        return '偏财' if ri_yang == ot_yang else '正财'
    
    # 克我
    if (ox, rx) in [('木','土'),('火','金'),('土','水'),('金','木'),('水','火')]:
        return '七杀' if ri_yang == ot_yang else '正官'
    
    return '?'


def print_shishen(result):
    """打印十神速查表"""
    rizhu = result['rizhu']
    print(f"【十神速查表·日主={rizhu}({WU_XING[rizhu]})】")
    print("-" * 50)
    
    stems = [
        ('年干', result['year'][0]),
        ('月干', result['month'][0]),
        ('日干', result['day'][0]),
        ('时干', result['hour'][0]),
    ]
    
    for pos_name, stem in stems:
        if pos_name == '日干':
            print(f"  {pos_name} {stem} → 日主")
        else:
            ss = get_shishen(rizhu, stem)
            print(f"  {pos_name} {stem} → {ss}")
    print()


def calc_qi_yun(year, month, day, direction):
    """计算起运年龄
    顺排：找出生后第一个换月节气，天数÷3=起运岁数
    逆排：找出生前最后一个换月节气，天数÷3=起运岁数
    返回：(起运年龄整数, 余数月数, 节气名称, 天数差)
    """
    birth = date(year, month, day)
    
    # 生成前后各一年的节气日期
    jieqi_dates = []
    for y in range(year - 1, year + 2):
        for jq_month, jq_day, name, _ in HUAN_YUE_JIE:
            try:
                jieqi_dates.append((date(y, jq_month, jq_day), name))
            except ValueError:
                pass
    
    jieqi_dates.sort()
    
    if direction == '顺排':
        for jq_date, name in jieqi_dates:
            if jq_date > birth:
                days = (jq_date - birth).days
                years = days // 3
                months = (days % 3) * 4  # 余数×4=月份
                return years, months, name, days
    else:
        last_jq = None
        for jq_date, name in jieqi_dates:
            if jq_date <= birth:
                last_jq = (jq_date, name)
        if last_jq:
            jq_date, name = last_jq
            days = (birth - jq_date).days
            years = days // 3
            months = (days % 3) * 4
            return years, months, name, days
    
    return 0, 0, '未知', 0


def print_da_yun(result, gender, birth_year, birth_month, birth_day):
    """计算大运并打印（含起运年龄和每步大运的起止年份）"""
    y_gan = result['year'][0]
    m_gan = result['month'][0]
    m_zhi = result['month'][1]
    
    yin_yang = '阳' if y_gan in YANG_GAN else '阴'
    
    # 大运顺逆：阳男阴女顺，阴男阳女逆
    if (yin_yang == '阳' and gender == '男') or (yin_yang == '阴' and gender == '女'):
        direction = '顺排'
        direction_label = '阳男顺排' if (yin_yang=='阳' and gender=='男') else '阴女顺排'
    else:
        direction = '逆排'
        direction_label = '阴男逆排' if (yin_yang=='阴' and gender=='男') else '阳女逆排'
    
    # 计算起运年龄
    qi_yun_years, qi_yun_months, jq_name, days_diff = calc_qi_yun(birth_year, birth_month, birth_day, direction)
    qi_yun_age = qi_yun_years + qi_yun_months / 12.0
    
    print(f"【大运排布】")
    print("-" * 50)
    print(f"  年干{y_gan}({yin_yang}) + 性别{gender} → {direction_label}")
    print(f"  出生到最近换月节气({jq_name})天数: {days_diff}天")
    print(f"  起运年龄: {qi_yun_years}岁{qi_yun_months}个月 (≈{qi_yun_age:.1f}岁)")
    print(f"  (注:节气日期每年±1天波动,起运为近似值)")
    print()
    
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
    
    # 计算每步大运起止年份
    for i, dy in enumerate(da_yun_list):
        start_age = qi_yun_age + i * 10
        end_age = qi_yun_age + (i + 1) * 10 - 0.01
        start_year = birth_year + int(start_age)
        end_year = birth_year + int(end_age)
        print(f"  {i+1}. {dy}  ({start_year}~{end_year}年  {start_age:.0f}~{int(end_age)}岁)")
    print()


def print_special_check(result):
    """特殊检查：高亮常见的易混淆陷阱"""
    print("【易混淆陷阱检查】")
    print("-" * 50)
    
    y_gan = result['year'][0]
    y_zhi = result['year'][1]
    r_gan = result['rizhu']
    r_zhi = result['day'][1]
    h_gan = result['hour'][0]
    
    rizhu_wuxing = WU_XING[r_gan]
    
    # 检查庚金对丙火的十神（易混淆点）
    for pos, stem in [('年干', result['year'][0]), ('月干', result['month'][0]), 
                       ('日干', result['day'][0]), ('时干', result['hour'][0])]:
        if stem == '庚' and r_gan == '丙':
            print(f"  ✅ {pos}庚金对丙火日主=偏财（不是七杀！丙火克庚金，阴阳相同）")
    
    # 检查壬水对丙火的十神
    for pos, stem in [('年干', result['year'][0]), ('月干', result['month'][0]),
                       ('日干', result['day'][0]), ('时干', result['hour'][0])]:
        if stem == '壬' and r_gan == '丙':
            print(f"  ✅ {pos}壬水对丙火日主=七杀（壬克丙，阴阳相同，这才是子星）")
    
    # 检查癸水对丙火的十神
        if stem == '癸' and r_gan == '丙':
            print(f"  ✅ {pos}癸水对丙火日主=正官（癸克丙，阴阳不同）")
    
    # 检查年支日支是否混淆
    print(f"  年支={y_zhi} 日支={r_zhi} → 确认没有互换？")
    
    # 检查巳的顺序
    for pos, zhi in [('年支', y_zhi), ('月支', result['month'][1]),
                     ('日支', r_zhi), ('时支', result['hour'][1])]:
        if zhi == '巳':
            cangs = CANG_GAN['巳']
            print(f"  ✅ {pos}巳的藏干顺序：丙(本100%)→戊(中60%)→庚(余30%) — 庚是最末余气")


# ============================================================
# 九、主函数
# ============================================================

def main():
    # 第一步：自检锚点
    verify_anchors()
    
    # 第二步：读入参数
    if len(sys.argv) >= 6:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        day = int(sys.argv[3])
        shichen_idx = int(sys.argv[4])
        gender = sys.argv[5]
    else:
        print("【输入八字信息】")
        try:
            year = int(input("  出生年(公历): "))
            month = int(input("  出生月: "))
            day = int(input("  出生日: "))
            print("  时辰: 0子 1丑 2寅 3卯 4辰 5巳 6午 7未 8申 9酉 10戌 11亥")
            shichen_idx = int(input("  时辰索引: "))
            gender = input("  性别(男/女): ").strip()
        except Exception as e:
            print(f"\n输入错误: {e}")
            print("使用默认示例：子源 2011-05-31 巳时 男")
            year, month, day, shichen_idx, gender = 2011, 5, 31, 5, '男'
    
    # 第三步：排盘
    result = calc_bazi(year, month, day, shichen_idx, gender)
    
    print("\n" + "=" * 66)
    print(f"  [八字] {result['bazi']}")
    print(f"  [日主] {result['rizhu']}({WU_XING[result['rizhu']]})")
    print("=" * 66)
    print()
    
    # 第五步：纳音
    print("【纳音】")
    print("-" * 50)
    pillars = [('年柱', result['year'][0], result['year'][1]),
               ('月柱', result['month'][0], result['month'][1]),
               ('日柱', result['day'][0], result['day'][1]),
               ('时柱', result['hour'][0], result['hour'][1])]
    for pname, g, z in pillars:
        print(f"  {pname} {g}{z} → {get_na_yin(g, z)}")
    print()
    
    # 第六步：藏干
    print_cang_gan(result)
    
    # 第七步：十神
    print_shishen(result)
    
    # 第八步：大运
    print_da_yun(result, gender, year, month, day)
    
    # 第九步：易混淆检查
    print_special_check(result)
    
    print()
    print("=" * 66)
    print("  🛡️  验证完成。请逐项核对以上内容。")
    print("  确认无误后再开始分析。")
    print("=" * 66)

if __name__ == '__main__':
    main()
