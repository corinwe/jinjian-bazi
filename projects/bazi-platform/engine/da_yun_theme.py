"""
大运十年主题定性模块 v1.0（2026-08-02·老板校准）

规则（duanming-siceng-luoji_20260802.md）：
  大运重地支，流年重天干
  大运=决定这10年是干嘛的（定性/主题/趋势）：
    - 结合大运地支五行→十神（对日主）+ 喜忌 → 定十年主题
    - 如：财(喜用)运=求财收获的十年；官杀(忌)运=压力打拼的十年；
        印运=学习沉淀的十年；食伤运=输出变现的十年；比劫运=合伙竞争防破财
  流年=应期：大运定10年基调，流年定具体年份的吉凶兑现
"""
from __future__ import annotations

from constants import BaZi, TIAN_GAN_WU_XING

ZHI_WX = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
          "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"}
GAN_WX = TIAN_GAN_WU_XING


def _zhi_shi_shen(zhi_wx: str, ri_zhu: str) -> str:
    """地支五行对日主的十神（大运定性用）"""
    ri_wx = GAN_WX.get(ri_zhu, "")
    sheng_mu = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    ke_mu = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    if zhi_wx == ri_wx:
        return "比劫"
    if sheng_mu.get(ri_wx) == zhi_wx:
        return "食伤"
    if sheng_mu.get(zhi_wx) == ri_wx:
        return "印"
    if ke_mu.get(zhi_wx) == ri_wx:
        return "官杀"
    if ke_mu.get(ri_wx) == zhi_wx:
        return "财"
    return "比劫"


def _theme_by_shi_shen(shi_shen: str, role: str) -> str:
    """十神+喜忌 → 十年主题"""
    if role == "喜用":
        themes = {
            "财": "求财收获的十年——主业发力、财富积累",
            "官杀": "建功立业的十年——事业进阶、担责掌权",
            "印": "学习沉淀的十年——进修考证、积累名誉",
            "食伤": "输出变现的十年——才华展露、技术/表达换钱",
            "比劫": "合伙开拓的十年——行动力强、合作共赢（防分利）",
        }
    elif role == "忌神":
        themes = {
            "财": "财来财去的十年——求财辛苦、防破耗",
            "官杀": "压力打拼的十年——担责受制、防官非（需制化）",
            "印": "思虑迟滞的十年——想法多行动少、防懒散（印重夺食）",
            "食伤": "输出受阻的十年——才华被抑、防口舌是非",
            "比劫": "竞争破财的十年——防争利、防借贷担保",
        }
    else:
        themes = {
            "财": "求财过渡的十年——财运平平、稳步积累",
            "官杀": "打拼过渡的十年——压力与机会并存",
            "印": "沉淀过渡的十年——学习与休整",
            "食伤": "输出过渡的十年——才华有发挥但一般",
            "比劫": "同行往来的十年——合作与竞争并存",
        }
    return themes.get(shi_shen, "过渡的十年")


def determine_da_yun_theme(da_yun_gan: str, da_yun_zhi: str, ri_zhu: str,
                           xi_yong: list[str], ji_shen: list[str]) -> dict:
    """大运十年主题定性

    返回: {
        "theme": 十年主题描述,
        "zhi_shi_shen": 地支十神,
        "zhi_role": "喜用"|"忌神"|"中性",
        "desc": 完整说明（大运重地支）
    }
    """
    zhi_wx = ZHI_WX.get(da_yun_zhi, "")
    zhi_ss = _zhi_shi_shen(zhi_wx, ri_zhu)

    if zhi_wx in xi_yong:
        role = "喜用"
    elif zhi_wx in ji_shen:
        role = "忌神"
    else:
        role = "中性"

    theme = _theme_by_shi_shen(zhi_ss, role)
    desc = f"大运{da_yun_gan}{da_yun_zhi}：地支{zhi_wx}为{zhi_ss}({role})→{theme}"

    return {
        "theme": theme,
        "zhi_shi_shen": zhi_ss,
        "zhi_role": role,
        "desc": desc,
    }
