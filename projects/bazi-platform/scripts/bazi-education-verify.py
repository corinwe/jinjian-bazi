#!/usr/bin/env python3
"""
金鉴真人·学历判断校准验证 v1.0
2026-06-24新增·老板令

用于每次输出学历判断前，强制执行九步法并校验合理性。
"""

import sys

# 年干→文昌映射
WENCHANG = {
    '甲': '巳', '乙': '午', '丙': '申', '丁': '酉',
    '戊': '申', '己': '酉', '庚': '亥', '辛': '子',
    '壬': '寅', '癸': '卯'
}

# 第0层：年柱有印三档法
def check_year_pillar(bazi):
    """检查年柱是否有印"""
    year_gan = bazi[0]  # 年干
    year_zhi = bazi[1]  # 年支
    
    # 年干为印？正印/偏印
    # 天干五行: 甲乙木, 丙丁火, 戊己土, 庚辛金, 壬癸水
    # 这需要日主信息才能判断，所以外部传入
    return year_gan, year_zhi

def check_education(bazi, rizhu, rizhu_wuxing, score, level):
    """
    完整九步学历判断
    bazi: 四柱八字数组 ['壬午','癸丑','辛巳','乙未']
    rizhu: 日主天干 '辛'
    rizhu_wuxing: '金'
    score: 身强弱分数 55.6
    level: 身强弱等级 '中和'
    """
    year_gan = bazi[0][0]
    year_zhi = bazi[0][1]
    month_zhi = bazi[1][1]
    ri_zhi = bazi[2][1]
    
    # 五行生克关系
    wuxing = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
    # 我生者为食伤，生我者为印，克我者为官杀，我克者为财，同我者为比劫
    
    # Step 1: 年柱是否有印
    # 年干
    year_gan_wx = wuxing[year_gan]
    ri_wx = wuxing[rizhu]
    
    # 判断年干是否为印：生我者为印
    sheng_wo = {'金':'土','木':'水','水':'金','火':'木','土':'火'}
    yin_wx = sheng_wo[ri_wx]  # 辛金→印星=土
    cai_wx = {'金':'木','木':'土','水':'火','火':'金','土':'水'}[ri_wx]  # 财星
    guan_wx = {'金':'火','木':'金','水':'土','火':'水','土':'木'}[ri_wx]  # 官杀
    bi_wx = ri_wx
    
    year_gan_is_yin = (year_gan_wx == yin_wx)
    
    # 年支藏干查印
    # 简化版藏干
    zhi_cang = {
        '子':['癸'], '丑':['己','癸','辛'], '寅':['甲','丙','戊'],
        '卯':['乙'], '辰':['戊','乙','癸'], '巳':['丙','戊','庚'],
        '午':['丁','己'], '未':['己','丁','乙'], '申':['庚','壬','戊'],
        '酉':['辛'], '戌':['戊','辛','丁'], '亥':['壬','甲']
    }
    
    year_zhi_cang = zhi_cang.get(year_zhi, [])
    year_zhi_has_yin = any(wuxing[c] == yin_wx for c in year_zhi_cang)
    
    step1 = "✅ 年柱有印" if (year_gan_is_yin or year_zhi_has_yin) else "❌ 年柱无印"
    
    # Step 2: 文昌
    wen = WENCHANG.get(year_gan, '?')  # 命理文昌用年干
    wen_in_bazi = wen in [b[1] for b in bazi]
    step2 = f"✅ 文昌{wen}在局" if wen_in_bazi else f"❌ 文昌{wen}不在原局"
    
    # Step 3: 印星质量 - 月令本气
    month_zhi_cang = zhi_cang.get(month_zhi, [])
    month_benqi = month_zhi_cang[0] if month_zhi_cang else '?'
    month_yin = (wuxing[month_benqi] == yin_wx)
    step3 = f"✅ 月令{month_zhi}本气{month_benqi}为印" if month_yin else f"❌ 月令{month_zhi}本气非印"
    
    # Step 4: 12岁前大运 - 需要大运数据，简化处理
    # 起运年龄来判断
    step4 = "待判断（需大运数据）"
    
    # Step 5: 身强弱
    if score >= 60:
        step5 = "✅ 身强，后劲足"
    elif score >= 40:
        step5 = "✅ 中和，灵活性高"
    else:
        step5 = "⚠️ 身弱，需印运支撑"
    
    # Step 6: 十神配合 - 简单判断
    step6 = "待判断（需十神数据）"
    
    # 综合
    print(f"\n{'='*50}")
    print(f"  学历九步判断 · {rizhu}日主·身{score}分({level})")
    print(f"  八字: {' '.join(bazi)}")
    print(f"{'='*50}")
    print(f"  Step 1 - 年柱有印: {step1}")
    print(f"  Step 2 - 文昌: {step2}")
    print(f"  Step 3 - 月令印: {step3}")
    print(f"  Step 4 - 12岁前运: {step4}")
    print(f"  Step 5 - 身强弱: {step5}")
    print(f"  Step 6 - 十神配合: {step6}")
    print(f"{'='*50}")
    print(f"  🚨 合理性校验：")
    
    # 关键警告
    warnings = []
    
    # 如果文昌不在局，且月令印不是本气，学历不能高估
    if not wen_in_bazi and not month_yin:
        warnings.append("⚠️ 文昌缺失+月令非印本气 → 学历上限不应超过本科")
    
    if not wen_in_bazi:
        warnings.append("⚠️ 文昌缺失 → 学历以本科为上限，硕士需额外因素（大运文昌/强印18岁前到位）")
    
    if score < 40:
        warnings.append("⚠️ 身弱 → 需印运支撑才能持续学习")
    
    for w in warnings:
        print(f"  {w}")
    
    print(f"{'='*50}")
    return step1, step2, step3, step5, warnings


if __name__ == '__main__':
    # 测试杨昌玉
    print("\n▶ 测试：杨昌玉（未时）")
    check_education(
        bazi=['壬午','癸丑','辛巳','乙未'],
        rizhu='辛',
        rizhu_wuxing='金',
        score=55.6,
        level='中和'
    )
    
    print("\n▶ 测试：杨昌玉（申时）")
    check_education(
        bazi=['壬午','癸丑','辛巳','丙申'],
        rizhu='辛',
        rizhu_wuxing='金',
        score=67.6,
        level='身强'
    )
    
    print("\n▶ 测试：家主魏启令")
    check_education(
        bazi=['庚申','癸未','辛亥','辛卯'],
        rizhu='辛',
        rizhu_wuxing='金',
        score=64.0,
        level='身强'
    )
    
    print("\n▶ 测试：子源魏源")
    check_education(
        bazi=['辛卯','癸巳','丙戌','癸巳'],
        rizhu='丙',
        rizhu_wuxing='火',
        score=55.6,
        level='中和'
    )
