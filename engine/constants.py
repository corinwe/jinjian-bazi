"""
金鉴真人·八字规则引擎 — 常量与类型定义
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ── 天干 ──
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
TIAN_GAN_YIN_YANG = {
    "甲": "阳",
    "乙": "阴",
    "丙": "阳",
    "丁": "阴",
    "戊": "阳",
    "己": "阴",
    "庚": "阳",
    "辛": "阴",
    "壬": "阳",
    "癸": "阴",
}

TIAN_GAN_WU_XING = {
    "甲": "木",
    "乙": "木",
    "丙": "火",
    "丁": "火",
    "戊": "土",
    "己": "土",
    "庚": "金",
    "辛": "金",
    "壬": "水",
    "癸": "水",
}

# 天干五行相生顺序: 木→火→土→金→水→木
# 天干五行相克顺序: 木克土, 土克水, 水克火, 火克金, 金克木

# ── 地支 ──
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
DI_ZHI_YIN_YANG = {
    "子": "阳",
    "丑": "阴",
    "寅": "阳",
    "卯": "阴",
    "辰": "阳",
    "巳": "阴",
    "午": "阳",
    "未": "阴",
    "申": "阳",
    "酉": "阴",
    "戌": "阳",
    "亥": "阴",
}

DI_ZHI_WU_XING = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}

# ── 地支藏干 (本气100%, 中气60%, 余气30%) ──
DI_ZHI_CANG_GAN: dict[str, list[tuple[str, int]]] = {
    "子": [("癸", 100)],
    "丑": [("己", 100), ("癸", 60), ("辛", 30)],
    "寅": [("甲", 100), ("丙", 60), ("戊", 30)],
    "卯": [("乙", 100)],
    "辰": [("戊", 100), ("乙", 60), ("癸", 30)],
    "巳": [("丙", 100), ("戊", 60), ("庚", 30)],
    "午": [("丁", 100), ("己", 60)],
    "未": [("己", 100), ("丁", 60), ("乙", 30)],
    "申": [("庚", 100), ("壬", 60), ("戊", 30)],
    "酉": [("辛", 100)],
    "戌": [("戊", 100), ("辛", 60), ("丁", 30)],
    "亥": [("壬", 100), ("甲", 60)],
}

# ── 藏干比例 (用于评分) ──
CANG_GAN_RATIO = {100: 1.0, 60: 0.6, 30: 0.3}
# 基础分: 年支=4, 月令=40, 日支=12, 时干=12, 时支=12
BASE_SCORE = {"年支": 4, "月令": 40, "日支": 12, "时干": 12, "时支": 12}

# ── 十神映射 ──
# 生我者 = 印（正印阴阳异，偏印同）
# 我生者 = 食伤（食神阴阳异，伤官同）
# 克我者 = 官杀（正官阴阳异，七杀同）
# 我克者 = 财（正财阴阳异，偏财同）
# 同我者 = 比劫（比肩同，劫财异）
SHI_SHEN_MAP = {
    ("生我", "异"): "正印",
    ("生我", "同"): "偏印",
    ("我生", "异"): "食神",
    ("我生", "同"): "伤官",
    ("克我", "异"): "正官",
    ("克我", "同"): "七杀",
    ("我克", "异"): "正财",
    ("我克", "同"): "偏财",
    ("同我", "同"): "比肩",
    ("同我", "异"): "劫财",
}

# ── 四柱位置 ──
PILLAR_NAMES = ["年柱", "月柱", "日柱", "时柱"]

# ── 纳音（简化版，按年柱查）──
# 完整60甲子纳音表
NA_YIN: dict[str, str] = {
    "甲子乙丑": "海中金",
    "丙寅丁卯": "炉中火",
    "戊辰己巳": "大林木",
    "庚午辛未": "路旁土",
    "壬申癸酉": "剑锋金",
    "甲戌乙亥": "山头火",
    "丙子丁丑": "涧下水",
    "戊寅己卯": "城头土",
    "庚辰辛巳": "白蜡金",
    "壬午癸未": "杨柳木",
    "甲申乙酉": "泉中水",
    "丙戌丁亥": "屋上土",
    "戊子己丑": "霹雳火",
    "庚寅辛卯": "松柏木",
    "壬辰癸巳": "长流水",
    "甲午乙未": "沙中金",
    "丙申丁酉": "山下火",
    "戊戌己亥": "平地木",
    "庚子辛丑": "壁上土",
    "壬寅癸卯": "金箔金",
    "甲辰乙巳": "覆灯火",
    "丙午丁未": "天河水",
    "戊申己酉": "大驿土",
    "庚戌辛亥": "钗钏金",
    "壬子癸丑": "桑柘木",
    "甲寅乙卯": "大溪水",
    "丙辰丁巳": "沙中土",
    "戊午己未": "天上火",
    "庚申辛酉": "石榴木",
    "壬戌癸亥": "大海水",
}

# ── 五行相生关系 ──
WU_XING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WU_XING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


# ── 核心数据类型 ──


@dataclass
class Pillar:
    """一柱"""

    gan: str  # 天干
    zhi: str  # 地支
    cang_gan: list[tuple[str, int]] = field(default_factory=list)

    def __post_init__(self):
        if not self.cang_gan:
            self.cang_gan = DI_ZHI_CANG_GAN.get(self.zhi, [])

    @property
    def gan_wu_xing(self) -> str:
        return TIAN_GAN_WU_XING[self.gan]

    @property
    def zhi_wu_xing(self) -> str:
        return DI_ZHI_WU_XING[self.zhi]


@dataclass
class BaZi:
    """八字四柱"""

    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar
    gender: str  # "男" or "女"

    @property
    def ri_zhu(self) -> str:
        """日主天干"""
        return self.day.gan

    @property
    def ri_zhu_wu_xing(self) -> str:
        return TIAN_GAN_WU_XING[self.ri_zhu]

    @property
    def ri_zhu_yin_yang(self) -> str:
        return TIAN_GAN_YIN_YANG[self.ri_zhu]

    def all_pillars(self) -> list[Pillar]:
        return [self.year, self.month, self.day, self.hour]

    def summary(self) -> str:
        return f"{self.year.gan}{self.year.zhi} {self.month.gan}{self.month.zhi} {self.day.gan}{self.day.zhi} {self.hour.gan}{self.hour.zhi}"


@dataclass
class DaYun:
    """一步大运"""

    gan: str  # 天干
    zhi: str  # 地支
    start_age: int  # 起始年龄
    end_age: int  # 结束年龄
    start_year: int  # 起始年份
    gan_zhi: str = ""  # 干支字符串

    def __post_init__(self):
        self.gan_zhi = f"{self.gan}{self.zhi}"

    @property
    def wu_xing(self) -> str:
        return f"{TIAN_GAN_WU_XING[self.gan]}{DI_ZHI_WU_XING[self.zhi]}"


@dataclass
class ScoreDetails:
    """评分明细"""

    yue_ling_yin: float = 0.0
    yue_ling_bi_jie: float = 0.0
    tian_gan_yin: float = 0.0
    tian_gan_bi_jie: float = 0.0
    ri_zhi_yin_bi: float = 0.0
    nian_shi_zhi_yin_bi: float = 0.0
    total: float = 0.0


@dataclass
class CaiXingDetail:
    """财星评分明细"""

    yue_ling_score: float = 0.0
    ri_zhi_score: float = 0.0
    shi_gan_score: float = 0.0
    shi_zhi_score: float = 0.0
    nian_zhi_score: float = 0.0
    total: float = 0.0
    is_yue_ling_ben_qi_cai: bool = False


@dataclass
class DimensionScore:
    """维度评分"""

    base: float = 0.0  # 原局基础 0-7
    da_yun_bonus: float = 0.0  # 大运赋能 0-3
    total: float = 0.0  # 总分 0-10


@dataclass
class ReportResult:
    """完整分析结果"""

    # 基础信息
    bazi: BaZi
    bazi_str: str = ""
    na_yin: list[str] = field(default_factory=list)

    # 身强弱
    shen_qiang_ruo_score: float = 0.0
    shen_qiang_ruo_label: str = ""  # "身强"/"身弱"/"从弱"/"从强"
    score_details: ScoreDetails = field(default_factory=ScoreDetails)

    # 财星
    cai_xing_score: float = 0.0
    cai_xing_detail: CaiXingDetail = field(default_factory=CaiXingDetail)

    # 格局
    ge_ju: str = ""
    ge_ju_detail: str = ""

    # 喜用神
    xi_yong_shen: list[str] = field(default_factory=list)  # 喜用五行
    ji_shen: list[str] = field(default_factory=list)  # 忌神五行

    # 大运
    da_yun_list: list[DaYun] = field(default_factory=list)
    best_da_yun: int | None = None  # 最佳大运index
    worst_da_yun: int | None = None  # 最差大运index

    # 8大维度
    dimensions: dict[str, DimensionScore] = field(default_factory=dict)

    # 十神明细
    shi_shen_detail: list[dict] = field(default_factory=list)
