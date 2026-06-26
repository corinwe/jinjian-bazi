"""
流年分析引擎 v1.0 — 金鉴真人·金鉴真人原始规则

流年断事步骤:
  第一步: 流年干支与大运干支的关系（冲刑合害）
  第二步: 流年干支与原局四柱的关系（冲刑合害）
  第三步: 流年十神定位（对日主的吉凶含义）
  第四步: 流年神煞（重点年份）
  第五步: 综合能量评估（大运+流年+原局的叠加）
"""

from __future__ import annotations
from typing import Optional, Tuple

from constants import (
    TIAN_GAN, DI_ZHI, TIAN_GAN_WU_XING, DI_ZHI_WU_XING,
    TIAN_GAN_YIN_YANG, WU_XING_SHENG, WU_XING_KE,
)
from shi_shen import get_shi_shen_for_gan
from xing_chong_he_hua import (
    check_all_relations, check_chong, check_xing,
    check_hai, check_liu_he, check_san_he, NENG_LIANG,
)
from shen_sha import ZAI_SHA, YUAN_CHEN


# ── 太岁 ──
TAI_SUI = {
    "子": "子", "丑": "丑", "寅": "寅", "卯": "卯",
    "辰": "辰", "巳": "巳", "午": "午", "未": "未",
    "申": "申", "酉": "酉", "戌": "戌", "亥": "亥",
}

# ── 犯太岁类型 ──
FAN_TAI_SUI = {
    "值太岁": 1.0,   # 本命年
    "冲太岁": 1.2,   # 六冲
    "刑太岁": 1.0,   # 三刑
    "害太岁": 0.8,   # 六害
    "破太岁": 0.6,   # 六破
}


def check_fan_tai_sui(year_zhi: str, liu_nian_zhi: str) -> Optional[Tuple[str, float]]:
    """检查犯太岁"""
    from xing_chong_he_hua import LIU_CHONG, SAN_XING, LIU_HAI
    
    # 值太岁（本命年）
    if liu_nian_zhi == year_zhi:
        return ("值太岁", FAN_TAI_SUI["值太岁"])
    
    # 冲太岁
    if LIU_CHONG.get(year_zhi) == liu_nian_zhi:
        return ("冲太岁", FAN_TAI_SUI["冲太岁"])
    
    # 刑太岁
    if year_zhi in SAN_XING and liu_nian_zhi in SAN_XING[year_zhi]:
        return ("刑太岁", FAN_TAI_SUI["刑太岁"])
    
    # 害太岁
    if LIU_HAI.get(year_zhi) == liu_nian_zhi:
        return ("害太岁", FAN_TAI_SUI["害太岁"])
    
    return None


def analyze_liu_nian(
    liu_nian_gan: str, liu_nian_zhi: str,
    ri_zhu: str, ri_zhu_wx: str,
    year_zhi: str,
    da_yun_gan: str, da_yun_zhi: str,
    all_zhi: list[str],
) -> dict:
    """
    分析流年
    返回完整结构
    """
    result = {
        "流年": f"{liu_nian_gan}{liu_nian_zhi}",
        "流年五行": TIAN_GAN_WU_XING[liu_nian_gan] + DI_ZHI_WU_XING[liu_nian_zhi],
        "流年十神": get_shi_shen_for_gan(liu_nian_gan, ri_zhu),
        "犯太岁": None,
        "与大运关系": "",
        "与原局关系": "",
        "综合评分": 5.0,
        "注意事项": [],
    }
    
    # 1. 犯太岁检查
    fan = check_fan_tai_sui(year_zhi, liu_nian_zhi)
    if fan:
        result["犯太岁"] = {"类型": fan[0], "能量": fan[1]}
        result["注意事项"].append(f"⚠️ {fan[0]}，注意防范")
    
    # 2. 流年与大运的关系
    dy_rel = check_all_relations([liu_nian_zhi, da_yun_zhi])
    result["与大运关系"] = dy_rel["summary"]
    if "冲" in dy_rel["summary"]:
        result["注意事项"].append("大运流年相冲，运势波动大")
    if "三合" in dy_rel["summary"]:
        result["注意事项"].append("大运流年三合，能量共振")
    
    # 3. 流年与原局的关系
    all_rels = check_all_relations(all_zhi + [liu_nian_zhi])
    result["与原局关系"] = all_rels["summary"]
    
    # 4. 综合评分
    score = 5.0
    # 流年十神为喜用加分
    liu_nian_ss = result["流年十神"]
    xi_yong_ss = ["正印", "偏印", "比肩", "劫财"]  # 简化
    ji_shen_ss = ["正财", "偏财", "正官", "七杀", "伤官"]  # 简化
    
    if liu_nian_ss in xi_yong_ss[:2]:  # 印星
        score += 2.0
    elif liu_nian_ss in xi_yong_ss[2:]:  # 比劫
        score += 1.0
    elif liu_nian_ss in ji_shen_ss[:2]:  # 财星
        score -= 1.0
    elif liu_nian_ss in ji_shen_ss[2:4]:  # 官杀
        score -= 1.5
    
    # 犯太岁减分
    if fan:
        score -= fan[1]
    
    # 冲大运减分
    if "冲" in dy_rel["summary"]:
        score -= 1.0
    
    result["综合评分"] = round(max(0, min(10, score)), 1)
    
    return result


def generate_liu_nian_years(birth_year: int, current_year: int, count: int = 10) -> list[int]:
    """生成流年年份列表"""
    return list(range(current_year, current_year + count))


def get_liu_nian_gan_zhi(year: int) -> Tuple[str, str]:
    """根据年份获取流年干支"""
    # 天干: 甲(4)乙(5)丙(6)丁(7)戊(8)己(9)庚(0)辛(1)壬(2)癸(3)
    tian_gan_idx = year % 10
    gan_map = {4: "甲", 5: "乙", 6: "丙", 7: "丁", 8: "戊", 9: "己", 0: "庚", 1: "辛", 2: "壬", 3: "癸"}
    # 地支: 子(0)丑(1)寅(2)卯(3)辰(4)巳(5)午(6)未(7)申(8)酉(9)戌(10)亥(11)
    di_zhi_idx = year % 12
    zhi_map = {0: "子", 1: "丑", 2: "寅", 3: "卯", 4: "辰", 5: "巳", 6: "午", 7: "未", 8: "申", 9: "酉", 10: "戌", 11: "亥"}
    return gan_map[tian_gan_idx], zhi_map[di_zhi_idx]


if __name__ == "__main__":
    # 测试: 家主 甲午 己巳 戊午 壬子, 大运乙亥(50-59岁)
    result = analyze_liu_nian("丙", "午", "戊", "土", "午", "乙", "亥", ["午", "巳", "午", "子"])
    print(f"流年分析:")
    for k, v in result.items():
        print(f"  {k}: {v}")
