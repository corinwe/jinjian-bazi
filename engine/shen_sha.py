"""
神煞系统引擎 v1.0 — 金鉴真人·金鉴真人原始规则

涵盖神煞:
  天乙贵人·文昌贵人·驿马·桃花(咸池)·华盖·天罗地网
  元辰·灾煞·劫煞·孤辰寡宿·红鸾天喜·天德月德
"""

from __future__ import annotations
from typing import Optional

# ── 天乙贵人 ──
# 甲戊庚牛羊, 乙己鼠猴乡, 丙丁猪鸡位, 壬癸兔蛇藏, 辛逢虎马
TIAN_YI = {
    "甲": ["丑", "未"], "戊": ["丑", "未"], "庚": ["丑", "未"],
    "乙": ["子", "申"], "己": ["子", "申"],
    "丙": ["亥", "酉"], "丁": ["亥", "酉"],
    "壬": ["卯", "巳"], "癸": ["卯", "巳"],
    "辛": ["寅", "午"],
}

# ── 文昌贵人 ──
# 甲巳乙午丙戊申, 丁己酉位庚亥辛, 壬寅癸卯顺推轮
WEN_CHANG = {
    "甲": "巳", "乙": "午", "丙": "申", "丁": "酉", "戊": "申",
    "己": "酉", "庚": "亥", "辛": "子", "壬": "寅", "癸": "卯",
}

# ── 驿马 ──
# 申子辰马在寅, 亥卯未马在巳, 寅午戌马在申, 巳酉丑马在亥
YI_MA = {
    "申": "寅", "子": "寅", "辰": "寅",
    "亥": "巳", "卯": "巳", "未": "巳",
    "寅": "申", "午": "申", "戌": "申",
    "巳": "亥", "酉": "亥", "丑": "亥",
}

# ── 桃花(咸池) ──
# 申子辰桃花在酉, 亥卯未桃花在子, 寅午戌桃花在卯, 巳酉丑桃花在午
TAO_HUA = {
    "申": "酉", "子": "酉", "辰": "酉",
    "亥": "子", "卯": "子", "未": "子",
    "寅": "卯", "午": "卯", "戌": "卯",
    "巳": "午", "酉": "午", "丑": "午",
}

# ── 华盖 ──
# 申子辰华盖在辰, 亥卯未华盖在未, 寅午戌华盖在戌, 巳酉丑华盖在丑
HUA_GAI = {
    "申": "辰", "子": "辰", "辰": "辰",
    "亥": "未", "卯": "未", "未": "未",
    "寅": "戌", "午": "戌", "戌": "戌",
    "巳": "丑", "酉": "丑", "丑": "丑",
}

# ── 天罗地网 ──
# 辰巳为天罗, 戌亥为地网
TIAN_LUO = ["辰", "巳"]
DI_WANG = ["戌", "亥"]

# ── 元辰(大耗) ──
# 阳男阴女: 冲年前进一位 = 对冲前一位
# 阴男阳女: 冲年后进一位 = 对冲后一位
# 简化: 年支对冲的下一个地支
YUAN_CHEN = {
    "子": "未", "丑": "申", "寅": "酉", "卯": "戌",
    "辰": "亥", "巳": "子", "午": "丑", "未": "寅",
    "申": "卯", "酉": "辰", "戌": "巳", "亥": "午",
}

# ── 灾煞 ──
# 申子辰灾煞在午, 亥卯未灾煞在酉, 寅午戌灾煞在子, 巳酉丑灾煞在卯
ZAI_SHA = {
    "申": "午", "子": "午", "辰": "午",
    "亥": "酉", "卯": "酉", "未": "酉",
    "寅": "子", "午": "子", "戌": "子",
    "巳": "卯", "酉": "卯", "丑": "卯",
}

# ── 劫煞 ──
# 申子辰劫煞在巳, 亥卯未劫煞在申, 寅午戌劫煞在亥, 巳酉丑劫煞在寅
JIE_SHA = {
    "申": "巳", "子": "巳", "辰": "巳",
    "亥": "申", "卯": "申", "未": "申",
    "寅": "亥", "午": "亥", "戌": "亥",
    "巳": "寅", "酉": "寅", "丑": "寅",
}

# ── 孤辰寡宿 ──
GU_CHEN_GUA_SU = {
    "子": ("寅", "戌"), "丑": ("寅", "戌"), "寅": ("巳", "丑"),
    "卯": ("巳", "丑"), "辰": ("巳", "丑"), "巳": ("申", "辰"),
    "午": ("申", "辰"), "未": ("申", "辰"), "申": ("亥", "未"),
    "酉": ("亥", "未"), "戌": ("亥", "未"), "亥": ("寅", "戌"),
}

# ── 天德月德 ──
TIAN_DE = {
    "子": "巳", "丑": "午", "寅": "未", "卯": "申",
    "辰": "酉", "巳": "戌", "午": "亥", "未": "子",
    "申": "丑", "酉": "寅", "戌": "卯", "亥": "辰",
}
YUE_DE = {
    "子": "壬", "丑": "庚", "寅": "丙", "卯": "甲",
    "辰": "壬", "巳": "庚", "午": "丙", "未": "甲",
    "申": "壬", "酉": "庚", "戌": "丙", "亥": "甲",
}


# ── 神煞解灾效果 ──
SHEN_SHA_JIE_ZAI = {
    "天乙贵人": 0.8,    # 遇难呈祥 80%
    "文昌贵人": 0.4,    # 学业加持 40%
    "天德": 0.7,        # 天德化解 70%
    "月德": 0.6,        # 月德化解 60%
}


def get_tian_yi(gan: str) -> list[str]:
    """获取天乙贵人"""
    return TIAN_YI.get(gan, [])

def get_wen_chang(gan: str) -> Optional[str]:
    """获取文昌贵人"""
    return WEN_CHANG.get(gan)

def get_yi_ma(zhi: str) -> Optional[str]:
    """获取驿马"""
    return YI_MA.get(zhi)

def get_tao_hua(zhi: str) -> Optional[str]:
    """获取桃花"""
    return TAO_HUA.get(zhi)

def get_hua_gai(zhi: str) -> Optional[str]:
    """获取华盖"""
    return HUA_GAI.get(zhi)

def check_tian_luo_di_wang(zhi: str) -> Optional[str]:
    """检查天罗地网"""
    if zhi in TIAN_LUO:
        return "天罗"
    if zhi in DI_WANG:
        return "地网"
    return None


class ShenShaResult:
    """神煞分析结果"""
    def __init__(self):
        self.tian_yi: list[str] = []
        self.wen_chang: list[str] = []
        self.yi_ma: list[str] = []
        self.tao_hua: list[str] = []
        self.hua_gai: list[str] = []
        self.tian_luo_di_wang: list[str] = []
        self.yuan_chen: list[str] = []
        self.zai_sha: list[str] = []
        self.jie_sha: list[str] = []
        self.gu_chen_gua_su: list[str] = []
        self.tian_de: list[str] = []
        self.yue_de: list[str] = []
        self.summary: str = ""
    
    def to_dict(self) -> dict:
        return {
            "天乙贵人": self.tian_yi,
            "文昌贵人": self.wen_chang,
            "驿马": self.yi_ma,
            "桃花": self.tao_hua,
            "华盖": self.hua_gai,
            "天罗地网": self.tian_luo_di_wang,
            "元辰": self.yuan_chen,
            "灾煞": self.zai_sha,
            "劫煞": self.jie_sha,
            "孤辰寡宿": self.gu_chen_gua_su,
            "天德": self.tian_de,
            "月德": self.yue_de,
            "summary": self.summary,
        }


def compute_all_shen_sha(bazi_gan_list: list[str], bazi_zhi_list: list[str],
                         year_zhi: str, month_zhi: str,
                         ri_gan: str) -> ShenShaResult:
    """
    计算全部神煞
    参数:
      bazi_gan_list: [年干, 月干, 日干, 时干]
      bazi_zhi_list: [年支, 月支, 日支, 时支]
    """
    result = ShenShaResult()
    
    # 天乙贵人（以日干、年干查）
    for gan in [ri_gan, bazi_gan_list[0]]:
        for gz in get_tian_yi(gan):
            if gz not in result.tian_yi:
                result.tian_yi.append(f"{gan}→{gz}")
    
    # 文昌贵人（以日干、年干查）
    for gan in [ri_gan, bazi_gan_list[0]]:
        wc = get_wen_chang(gan)
        if wc:
            result.wen_chang.append(f"{gan}→{wc}")
    
    # 驿马（以年支、日支查）
    for zhi in [year_zhi, bazi_zhi_list[2]]:
        ym = get_yi_ma(zhi)
        if ym:
            result.yi_ma.append(f"{zhi}→{ym}")
    
    # 桃花（以年支查）
    th = get_tao_hua(year_zhi)
    if th:
        result.tao_hua.append(f"{year_zhi}→{th}")
    
    # 华盖（以年支查）
    hg = get_hua_gai(year_zhi)
    if hg:
        result.hua_gai.append(f"{year_zhi}→{hg}")
    
    # 天罗地网（查日支、年支）
    for zhi in [bazi_zhi_list[2], year_zhi]:
        tldw = check_tian_luo_di_wang(zhi)
        if tldw:
            result.tian_luo_di_wang.append(f"{zhi}→{tldw}")
    
    # 元辰（以年支查）
    yc = YUAN_CHEN.get(year_zhi)
    if yc:
        result.yuan_chen.append(f"{year_zhi}→{yc}")
    
    # 灾煞（以年支查）
    zs = ZAI_SHA.get(year_zhi)
    if zs:
        result.zai_sha.append(f"{year_zhi}→{zs}")
    
    # 劫煞（以年支查）
    js = JIE_SHA.get(year_zhi)
    if js:
        result.jie_sha.append(f"{year_zhi}→{js}")
    
    # 孤辰寡宿（以年支查）
    gcgs = GU_CHEN_GUA_SU.get(year_zhi)
    if gcgs:
        result.gu_chen_gua_su.append(f"孤辰{year_zhi}→{gcgs[0]}")
        result.gu_chen_gua_su.append(f"寡宿{year_zhi}→{gcgs[1]}")
    
    # 天德（以月支查）
    td = TIAN_DE.get(month_zhi)
    if td:
        result.tian_de.append(f"{month_zhi}→{td}")
    
    # 月德（以月支查）
    yd = YUE_DE.get(month_zhi)
    if yd:
        result.yue_de.append(f"{month_zhi}→{yd}")
    
    # 汇总
    parts = []
    if result.tian_yi: parts.append(f"天乙: {','.join(result.tian_yi)}")
    if result.wen_chang: parts.append(f"文昌: {','.join(result.wen_chang)}")
    if result.yi_ma: parts.append(f"驿马: {','.join(result.yi_ma)}")
    if result.tao_hua: parts.append(f"桃花: {','.join(result.tao_hua)}")
    if result.hua_gai: parts.append(f"华盖: {','.join(result.hua_gai)}")
    if result.tian_luo_di_wang: parts.append(f"天罗地网: {','.join(result.tian_luo_di_wang)}")
    result.summary = " | ".join(parts) if parts else "无明显神煞"
    
    return result


if __name__ == "__main__":
    # 测试: 子源 庚申 辛巳 甲午 丙寅
    gans = ["庚", "辛", "甲", "丙"]
    zhis = ["申", "巳", "午", "寅"]
    result = compute_all_shen_sha(gans, zhis, "申", "巳", "甲")
    print(f"神煞分析:")
    for k, v in result.to_dict().items():
        print(f"  {k}: {v}")
