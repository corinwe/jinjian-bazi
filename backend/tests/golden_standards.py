"""
金鉴真人引擎 - 金标准数据
从知识库人物档案(2026-06-27更新)提取
"""
import sys; sys.path.insert(0, '/root/jinjian/backend')
from app.services.bazi_engine import TIAN_GAN, DI_ZHI, NA_YIN

# 每条用例: (标签, 年,月,日,时,分,性别, 金标准dict)
CASES = [
    {
        "name": "老板 (魏启令)",
        "y": 1980, "m": 8, "d": 6, "h": 5, "min": 0, "gender": 1,
        "golden": {
            "ba_zi": "庚申 癸未 辛亥 辛卯",
            "na_yin": ["石榴木", "杨柳木", "钗钏金", "松柏木"],
            "shen_qiang_level": "身强", "shen_qiang_score": 64.0,
            "ge_ju": "偏印格",
            "xi_shen": ["火","木","水"], "ji_shen": ["土","金"],
            "cai_xing_score": 31.2, "cai_xing_level": "小富",
            "da_yun_start": "甲申", "qi_yun_age": 0.0,
            "da_yun_sequence": ["甲申","乙酉","丙戌","丁亥","戊子","己丑","庚寅","辛卯"],
        }
    },
    {
        "name": "少爷 (魏源/Joe)",
        "y": 2011, "m": 5, "d": 31, "h": 9, "min": 9, "gender": 1,
        "golden": {
            "ba_zi": "辛卯 癸巳 丙戌 癸巳",
            "na_yin": ["松柏木", "长流水", "屋上土", "长流水"],
            "shen_qiang_level": "中和", "shen_qiang_score": 55.6,
            "ge_ju": "正官格",
            "xi_shen": ["水","金","土"], "ji_shen": ["木","火"],
            "cai_xing_score": 30.8, "cai_xing_level": "小富",
            "da_yun_start": "壬辰", "qi_yun_age": 9.1,
            "da_yun_sequence": ["壬辰","辛卯","庚寅","己丑","戊子","丁亥","丙戌","乙酉"],
        }
    },
    {
        "name": "主母 (刘成)",
        "y": 1987, "m": 7, "d": 20, "h": 12, "min": 0, "gender": 0,
        "golden": {
            "ba_zi": "丁卯 丁未 庚午 壬午",
            "na_yin": ["炉中火", "天河水", "路旁土", "杨柳木"],
            "shen_qiang_level": "从弱", "shen_qiang_score": 50.0,
            "ge_ju": "正印格",
            "xi_shen": ["火","木","水"], "ji_shen": ["土","金"],
            "cai_xing_score": 16.0, "cai_xing_level": "小富",
            "da_yun_start": "戊申", "qi_yun_age": 0.4,
            "da_yun_sequence": ["戊申","己酉","庚戌","辛亥","壬子","癸丑","甲寅","乙卯"],
        }
    },
]
