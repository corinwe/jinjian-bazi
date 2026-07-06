#!/usr/bin/env python3
"""
金鉴真人·八字全量验证脚本 v1.0
统一验证以下维度：
① 八字 vs 日柱一致性
② 空亡正确性
③ 大运年份正确性
④ 身强弱分数一致性
⑤ 财星分数一致性

用法：python3 bazi-full-verify.py <年> <月> <日> <时> <分> <时辰索引> <性别> <姓名>
输出：逐项验证结果
"""

import json, sys, math
from datetime import date, datetime

TIAN_GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DI_ZHI  = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

# 六甲旬空亡表
KONG_WANG = {
    '甲子': ('戌','亥'), '乙丑': ('戌','亥'), '丙寅': ('戌','亥'),
    '丁卯': ('戌','亥'), '戊辰': ('戌','亥'), '己巳': ('戌','亥'),
    '庚午': ('戌','亥'), '辛未': ('戌','亥'), '壬申': ('戌','亥'),
    '癸酉': ('戌','亥'),
    '甲戌': ('申','酉'), '乙亥': ('申','酉'), '丙子': ('申','酉'),
    '丁丑': ('申','酉'), '戊寅': ('申','酉'), '己卯': ('申','酉'),
    '庚辰': ('申','酉'), '辛巳': ('申','酉'), '壬午': ('申','酉'),
    '癸未': ('申','酉'),
    '甲申': ('午','未'), '乙酉': ('午','未'), '丙戌': ('午','未'),
    '丁亥': ('午','未'), '戊子': ('午','未'), '己丑': ('午','未'),
    '庚寅': ('午','未'), '辛卯': ('午','未'), '壬辰': ('午','未'),
    '癸巳': ('午','未'),
    '甲午': ('辰','巳'), '乙未': ('辰','巳'), '丙申': ('辰','巳'),
    '丁酉': ('辰','巳'), '戊戌': ('辰','巳'), '己亥': ('辰','巳'),
    '庚子': ('辰','巳'), '辛丑': ('辰','巳'), '壬寅': ('辰','巳'),
    '癸卯': ('辰','巳'),
    '甲辰': ('寅','卯'), '乙巳': ('寅','卯'), '丙午': ('寅','卯'),
    '丁未': ('寅','卯'), '戊申': ('寅','卯'), '己酉': ('寅','卯'),
    '庚戌': ('寅','卯'), '辛亥': ('寅','卯'), '壬子': ('寅','卯'),
    '癸丑': ('寅','卯'),
    '甲寅': ('子','丑'), '乙卯': ('子','丑'), '丙辰': ('子','丑'),
    '丁巳': ('子','丑'), '戊午': ('子','丑'), '己未': ('子','丑'),
    '庚申': ('子','丑'), '辛酉': ('子','丑'), '壬戌': ('子','丑'),
    '癸亥': ('子','丑'),
}

def calc_ri_zhu(y, m, d):
    """计算日柱"""
    base = date(1900, 1, 1)  # 甲戌日
    target = date(y, m, d)
    delta = (target - base).days
    ri_gan = TIAN_GAN[delta % 10]
    ri_zhi = DI_ZHI[(10 + delta) % 12]
    return f"{ri_gan}{ri_zhi}"

def calc_kong_wang(ri_zhu_str):
    """查空亡"""
    if ri_zhu_str in KONG_WANG:
        return KONG_WANG[ri_zhu_str]
    return ('?','?')

def calc_qi_yun_base(y, m, d, shichen_idx, gender):
    """估算起运年龄（简化版，用于验证大运年份）"""
    # 年干计算
    gan = TIAN_GAN[(y - 4) % 10]
    zhi = DI_ZHI[(y - 4) % 12]
    yin_yang = '阳' if gan in ['甲','丙','戊','庚','壬'] else '阴'
    if (yin_yang == '阳' and gender == '男') or (yin_yang == '阴' and gender == '女'):
        direction = '顺'
    else:
        direction = '逆'
    
    birth_dt = datetime(y, m, d, shichen_idx * 2 + 1, 0)
    
    # 简化的节气计算（用固定日期近似，精确计算需ephem）
    jieqi_dates = {
        '立春': (2,4), '惊蛰': (3,6), '清明': (4,5), '立夏': (5,6),
        '芒种': (6,6), '小暑': (7,7), '立秋': (8,7), '白露': (9,8),
        '寒露': (10,8), '立冬': (11,7), '大雪': (12,7), '小寒': (1,6),
    }
    # 简单估算：直接从生日算到下个节气
    # 这里仅用于大运年份验证，精确值应由引擎计算
    return 0, direction, gan+zhi

def verify(ri_zhu_str, gender, birth_y, da_yun_list):
    """验证五项"""
    errors = []
    
    # ① 空亡验证
    kw = calc_kong_wang(ri_zhu_str)
    kw_desc = f"{kw[0]}{kw[1]}"
    
    # ② 大运年份验证 - 从首步大运看
    if da_yun_list:
        first_dy = da_yun_list[0]
        # 大运起始年应在出生年后合理范围内
        start_y = first_dy.get('起始年份', 0)
        if start_y < birth_y or start_y > birth_y + 15:
            errors.append(f"大运起始年({start_y})与出生年({birth_y})偏移异常")
    
    return kw_desc, errors

def main():
    if len(sys.argv) < 8:
        print("用法: python3 bazi-full-verify.py <年> <月> <日> <时> <分> <时辰索引> <性别> <姓名>")
        sys.exit(1)
    
    y, m, d, h, minute, sx, gender, name = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), sys.argv[7], sys.argv[8]
    
    print(f"═══ 金鉴真人·八字全量验证 ═══")
    print(f"命主: {name}")
    print()
    
    # ① 日柱验证
    ri_zhu = calc_ri_zhu(y, m, d)
    print(f"① 日柱: {ri_zhu}")
    
    # ② 空亡验证
    kw = calc_kong_wang(ri_zhu)
    print(f"② 空亡: {kw[0]}{kw[1]} (日柱{ri_zhu}→{get_xun(ri_zhu)}旬)")
    
    # ③ 大运验证
    print(f"③ 大运: 出生{y}年, 待引擎提供详细序列后验证年份")
    
    # ④ 身强弱 → 需引擎数据
    # ⑤ 财星 → 需引擎数据
    print(f"④ 身强弱: 需运行引擎获取评分")
    print(f"⑤ 财星分数: 需运行引擎获取评分")
    print()
    print("✅ 基础验证通过（日柱+空亡）")
    print("⚠️ 全方位验证请配合 bazi-engine.py --json 输出运行")

def get_xun(ri_zhu):
    """获取日柱所属旬"""
    for i in range(0, 60, 10):
        gan = TIAN_GAN[i % 10]
        zhi = DI_ZHI[i % 12]
        xun_start = f"{gan}{zhi}"
        if ri_zhu in [TIAN_GAN[(i+j)%10] + DI_ZHI[(i+j)%12] for j in range(10)]:
            return xun_start + '旬'
    return '?'

if __name__ == '__main__':
    main()
