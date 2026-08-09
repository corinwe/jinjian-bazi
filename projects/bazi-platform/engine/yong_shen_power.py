"""
喜用神力量评估模块 v1.0（2026-08-02·荀太虚三步断运法第二步）

规则来源：《荀太虚断命方法论》taixu-duanming-method_20260802.md
核心：喜用神在原局的力量决定格局高低与大起大落程度
  喜用有力 → 成就格局不低，大起大落程度轻
  喜用缺/弱/被扰 → 成就等运催，容易大起大落（运来上去，运走下来）
"""
from __future__ import annotations

from constants import BaZi, Pillar, TIAN_GAN_WU_XING

# 天干五行
GAN_WX = TIAN_GAN_WU_XING
# 地支藏干本气五行
ZHI_WX = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
          "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"}

# 五行生克
SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


def assess_yong_shen_power(bazi: BaZi, xi_yong: list[str]) -> dict:
    """评估喜用神在原局的力量

    返回: {
        "level": "强"|"中"|"弱"|"缺失",
        "detail": 详细说明,
        "score": 0-100,
        "da_qi_da_luo": "轻微"|"中等"|"严重"  大起大落程度
    }
    """
    if not xi_yong:
        return {"level": "缺失", "detail": "无喜用神可评估", "score": 0, "da_qi_da_luo": "严重"}

    gans = [bazi.year.gan, bazi.month.gan, bazi.day.gan, bazi.hour.gan]
    zhis = [bazi.year.zhi, bazi.month.zhi, bazi.day.zhi, bazi.hour.zhi]
    pos_names = ["年", "月", "日", "时"]

    detail_parts = []
    total_score = 0
    wuxing_scores = {}

    for wx in xi_yong:
        score = 0
        parts = []
        # 1. 天干透出（透干=强）
        tou = [g for g in gans if GAN_WX.get(g) == wx]
        if tou:
            score += 30
            parts.append(f"{wx}透干({','.join(tou)})")
        # 2. 地支有根（藏干同五行=根）
        gen = [zhis[i] for i in range(4) if ZHI_WX.get(zhis[i]) == wx]
        if gen:
            score += 20 + 10 * len(gen)
            parts.append(f"{wx}地支有根({','.join(gen)})")
        # 3. 被生（生它的五行在局中=源头）
        sheng_wx = SHENG.get(wx)
        if sheng_wx:
            sheng_count = sum(1 for g in gans if GAN_WX.get(g) == sheng_wx) + \
                          sum(1 for z in zhis if ZHI_WX.get(z) == sheng_wx)
            if sheng_count > 0:
                score += min(20, sheng_count * 5)
                parts.append(f"{wx}有{sheng_wx}生({sheng_count}处)")
        # 4. 被克（克它的五行=干扰）
        ke_wx = KE.get(wx)
        if ke_wx:
            ke_count = sum(1 for g in gans if GAN_WX.get(g) == ke_wx) + \
                       sum(1 for z in zhis if ZHI_WX.get(z) == ke_wx)
            if ke_count > 0:
                score -= min(25, ke_count * 8)
                parts.append(f"{wx}被{ke_wx}克({ke_count}处)")
        wuxing_scores[wx] = max(0, score)
        total_score += max(0, score)
        detail_parts.append(f"{wx}:{'+'.join(parts) if parts else '无根无透'}")

    # 综合评级（取最强喜用的分数）
    best = max(wuxing_scores.values()) if wuxing_scores else 0
    if best >= 50:
        level = "强"
        da_qi = "轻微"
    elif best >= 25:
        level = "中"
        da_qi = "中等"
    elif best > 0:
        level = "弱"
        da_qi = "严重"
    else:
        level = "缺失"
        da_qi = "严重"

    return {
        "level": level,
        "detail": "；".join(detail_parts),
        "score": best,
        "da_qi_da_luo": da_qi,
        "wuxing_scores": wuxing_scores,
    }


def check_tong_guan_duan(bazi: BaZi, xi_yong: list[str]) -> str:
    """关键通关断检测（老板校准·2026-08-02）

    规则：喜用链条（通关）是否被截断
      食伤生财：食伤(金)生财(水)——水生木？按五行生克查链条
      杀印相生：官杀(木)生印(火)——木生火
      伤官配印：伤官(金)佩印(火)——金被火制=配印
    返回: 通关状态描述
    """
    gans = [bazi.year.gan, bazi.month.gan, bazi.day.gan, bazi.hour.gan]
    zhis = [bazi.year.zhi, bazi.month.zhi, bazi.day.zhi, bazi.hour.zhi]
    wuxing_counts = {}
    for g in gans:
        wuxing_counts[GAN_WX.get(g, "")] = wuxing_counts.get(GAN_WX.get(g, ""), 0) + 1
    for z in zhis:
        wuxing_counts[ZHI_WX.get(z, "")] = wuxing_counts.get(ZHI_WX.get(z, ""), 0) + 1

    # 关键通关链（按喜用判断主线）
    chain_desc = []
    # 食伤→财链：金生水（食伤金→财水）
    if "金" in xi_yong and "水" in xi_yong:
        jin = wuxing_counts.get("金", 0)
        shui = wuxing_counts.get("水", 0)
        huo = wuxing_counts.get("火", 0)
        if jin > 0 and shui > 0:
            if huo >= 3:
                chain_desc.append(f"食伤生财链(金→水)被火克截断(火{huo}处)")
            else:
                chain_desc.append(f"食伤生财链(金→水)通畅(金{jin}水{shui})")
        elif shui == 0:
            chain_desc.append("食伤生财链断：原局无财(水)")
    # 杀印相生链：木生火（官杀木→印火）
    if "木" in xi_yong and "火" in xi_yong:
        mu = wuxing_counts.get("木", 0)
        huo = wuxing_counts.get("火", 0)
        if mu > 0 and huo > 0:
            chain_desc.append(f"杀印相生链(木→火)存在(木{mu}火{huo})")
        elif mu == 0:
            chain_desc.append("杀印相生链断：原局无官杀(木)")

    return "；".join(chain_desc) if chain_desc else "无典型通关链"


def determine_ge_ju_level(bazi: BaZi, xi_yong: list[str], ji_shen: list[str]) -> dict:
    """原局格局层次三档判定（老板校准·2026-08-02）

    (a) 原局有用神且未被破坏 → 格局层次不低（高）
    (b) 喜用神被破坏 → 层次打折扣（中）
    (c) 原局没有喜用神 → 格局很低（低）
    返回: {"level": "高"|"中"|"低", "reason": 判定理由, "xi_yong_power": ..., "tong_guan": ...}
    """
    power = assess_yong_shen_power(bazi, xi_yong)
    tong_guan = check_tong_guan_duan(bazi, xi_yong)

    # 判断喜用是否被破坏：喜用力量弱 + 被克 + 冲用神
    broken_parts = []
    if power["level"] == "缺失":
        return {"level": "低", "reason": f"原局无喜用神({','.join(xi_yong) if xi_yong else '无'})→格局很低",
                "xi_yong_power": power, "tong_guan": tong_guan}
    if power["level"] == "弱":
        broken_parts.append(f"喜用力量弱({power['score']}分)")
    # 被克检测（喜用五行被忌神克）
    for wx in xi_yong:
        ke_wx = KE.get(wx)
        if ke_wx and ke_wx in ji_shen:
            ke_count = sum(1 for g in [bazi.year.gan, bazi.month.gan, bazi.day.gan, bazi.hour.gan] if GAN_WX.get(g) == ke_wx) + \
                        sum(1 for z in [bazi.year.zhi, bazi.month.zhi, bazi.day.zhi, bazi.hour.zhi] if ZHI_WX.get(z) == ke_wx)
            if ke_count >= 2:
                broken_parts.append(f"{wx}喜用被{ke_wx}忌神克({ke_count}处)")
    # 通关断检测
    if "断" in tong_guan or "截断" in tong_guan:
        broken_parts.append(f"通关断: {tong_guan}")

    if not broken_parts and power["level"] in ("强", "中"):
        return {"level": "高", "reason": f"原局有喜用({','.join(xi_yong)})且未被破坏→格局层次不低",
                "xi_yong_power": power, "tong_guan": tong_guan}
    elif power["level"] == "强" and len(broken_parts) <= 1:
        # 喜用强但轻度受扰 → 中偏高
        return {"level": "中", "reason": f"喜用有力但受扰: {'；'.join(broken_parts)}→层次打折扣",
                "xi_yong_power": power, "tong_guan": tong_guan}
    else:
        return {"level": "中", "reason": f"喜用被破坏: {'；'.join(broken_parts) if broken_parts else '力量弱'}→层次打折扣",
                "xi_yong_power": power, "tong_guan": tong_guan}


def assess_ji_shen_zuoshi(bazi: BaZi, ji_shen: list[str], xi_yong: list[str] | None = None,
                          liu_nian_gan: str | None = None,
                          liu_nian_zhi: str | None = None) -> dict:
    """忌神得力检测（荀太虚第三步·流年版）

    规则：
      忌神得力（地支生它/天干坐实/三合引动）→ 该年份不好
    返回: {
        "ji_shen_zuo_shi": bool,  流年忌神是否坐实
        "san_he_yin_dong": str,   忌神三合引动描述
        "level": "高"|"中"|"低",
        "desc": 说明
    }
    """
    if not ji_shen:
        return {"ji_shen_zuo_shi": False, "san_he_yin_dong": "", "level": "低", "desc": "无忌神"}

    gans = [bazi.year.gan, bazi.month.gan, bazi.day.gan, bazi.hour.gan]
    zhis = [bazi.year.zhi, bazi.month.zhi, bazi.day.zhi, bazi.hour.zhi]
    pos_names = ["年", "月", "日", "时"]

    desc_parts = []
    zuoshi = False
    sanhe_desc = ""
    level_score = 0

    for wx in ji_shen:
        parts = []
        # 原局忌神状态
        tou = [g for g in gans if GAN_WX.get(g) == wx]
        gen = [zhis[i] for i in range(4) if ZHI_WX.get(zhis[i]) == wx]
        if tou:
            parts.append(f"原局{wx}透干({','.join(tou)})")
        if gen:
            parts.append(f"原局{wx}有根({','.join(gen)})")
        # 流年忌神
        if liu_nian_gan and GAN_WX.get(liu_nian_gan) == wx:
            parts.append(f"流年{liu_nian_gan}透{wx}坐实")
            zuoshi = True
            level_score += 2
        if liu_nian_zhi and ZHI_WX.get(liu_nian_zhi) == wx:
            parts.append(f"流年{liu_nian_zhi}地支{wx}坐实")
            zuoshi = True
            level_score += 2
        if parts:
            desc_parts.append(f"{wx}:{'、'.join(parts)}")

    # 三合引动检测（流年地支与原局地支成三合且为忌神）
    if liu_nian_zhi:
        sanhe_map = {
            ("寅", "午", "戌"): "火", ("申", "子", "辰"): "水",
            ("亥", "卯", "未"): "木", ("巳", "酉", "丑"): "金",
        }
        for trio, wx in sanhe_map.items():
            if liu_nian_zhi in trio:
                # 原局中该局的其他支
                present = [z for z in zhis if z in trio and z != liu_nian_zhi]
                if len(present) == 2:  # 完整三合
                    if wx in ji_shen:
                        sanhe_desc = f"流年{liu_nian_zhi}与原局{''.join(present)}三合{wx}局(忌神引动!)"
                        level_score += 3
                    else:
                        sanhe_desc = f"流年{liu_nian_zhi}与原局{''.join(present)}三合{wx}局"
                        level_score += 1
                elif len(present) == 1:  # 半合
                    if wx in ji_shen:
                        sanhe_desc = f"流年{liu_nian_zhi}与原局{present[0]}半合{wx}局(忌神)"
                        level_score += 1

    # 冲用神检测（荀太虚2022案例：寅申冲=掐财源/喜用根被冲）
    chong_desc = ""
    chong_map = {"子": "午", "午": "子", "丑": "未", "未": "丑", "寅": "申", "申": "寅",
                 "卯": "酉", "酉": "卯", "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳"}
    if liu_nian_zhi and xi_yong:
        # 流年支冲原局喜用根
        for i, z in enumerate(zhis):
            if chong_map.get(liu_nian_zhi) == z:
                z_wx = ZHI_WX.get(z, "")
                if z_wx in xi_yong:
                    chong_desc = f"流年{liu_nian_zhi}冲{pos_names[i]}支{z}({z_wx}喜用根被冲!)"
                    level_score += 3
                else:
                    chong_desc = f"流年{liu_nian_zhi}冲{pos_names[i]}支{z}"
                    level_score += 1
        # 流年支冲大运/冲日支（日支=自己）
        if chong_map.get(liu_nian_zhi) == bazi.day.zhi:
            d_wx = ZHI_WX.get(bazi.day.zhi, "")
            if d_wx in xi_yong:
                chong_desc += f"；冲日支{bazi.day.zhi}({d_wx}喜用)"
                level_score += 2
    # 喜用透出被忌神克（2022壬水被火反克案例）
    if liu_nian_gan and xi_yong and GAN_WX.get(liu_nian_gan) in xi_yong:
        lw = GAN_WX[liu_nian_gan]
        ke_lw = KE.get(lw)  # 克喜用的五行
        if ke_lw:
            ke_count = sum(1 for g in gans if GAN_WX.get(g) == ke_lw) + \
                       sum(1 for z in zhis if ZHI_WX.get(z) == ke_lw)
            if ke_count >= 3:  # 原局忌神多，喜用透出反被克
                chong_desc += f"；{liu_nian_gan}({lw}喜用)透出被{ke_lw}克({ke_count}处)"
                level_score += 2

    if level_score >= 4:
        level = "高"
    elif level_score >= 2:
        level = "中"
    else:
        level = "低"

    return {
        "ji_shen_zuo_shi": zuoshi,
        "san_he_yin_dong": sanhe_desc,
        "level": level,
        "desc": "；".join(desc_parts) if desc_parts else "忌神未得力",
    }
