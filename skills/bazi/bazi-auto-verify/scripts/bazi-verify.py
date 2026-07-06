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

# 基础常量
TIAN_GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DI_ZHI   = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
BASE_DATE = date(1900, 1, 1)
BASE_GAN = 0   # 甲
BASE_ZHI = 10  # 戌

# 藏干表（60/30/10标准·用户逐字确认版）
CANG_GAN = {
    '子': [('癸', 100)],
    '丑': [('己', 60), ('癸', 30), ('辛', 10)],
    '寅': [('甲', 60), ('丙', 30), ('戊', 10)],
    '卯': [('乙', 100)],
    '辰': [('戊', 60), ('乙', 30), ('癸', 10)],
    '巳': [('丙', 60), ('戊', 30), ('庚', 10)],  # ✅ 庚=余气10%，不是中气
    '午': [('丁', 60), ('己', 30)],
    '未': [('己', 60), ('丁', 30), ('乙', 10)],
    '申': [('庚', 60), ('壬', 30), ('戊', 10)],
    '酉': [('辛', 100)],
    '戌': [('戊', 60), ('辛', 30), ('丁', 10)],  # ✅ 辛=中气30%
    '亥': [('壬', 60), ('甲', 30)],
}

def calc_rizhu(target_date):
    delta = (target_date - BASE_DATE).days
    return TIAN_GAN[(BASE_GAN + delta) % 10], DI_ZHI[(BASE_ZHI + delta) % 12]

def calc_bazi(year, month, day, shichen_idx, gender):
    target = date(year, month, day)
    y_gan = TIAN_GAN[(year - 4) % 10]
    y_zhi = DI_ZHI[(year - 4) % 12]
    # 此处为简化版，完整版见 bazi-engine.py
    r_gan, r_zhi = calc_rizhu(target)
    shi_zhi = DI_ZHI[shichen_idx]
    return {'bazi': f"{y_gan}{y_zhi} ??? {r_gan}{r_zhi} ??? {shi_zhi}", 'rizhu': r_gan}

print("此脚本为简化验证版，完整引擎见 bazi-engine.py")
print("用法：python3 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-verify.py [年] [月] [日] [时辰] [性别]")
