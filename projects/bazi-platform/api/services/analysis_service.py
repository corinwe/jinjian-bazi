"""分析业务逻辑服务"""

import json

from api.repositories.analysis_repo import AnalysisRepository
from api.repositories.user_repo import UserRepository
from api.services.engine_client import call_engine


class AnalysisService:
    """八字分析业务逻辑"""

    def __init__(self):
        self.user_repo = UserRepository()
        self.analysis_repo = AnalysisRepository()

    def analyze(
        self,
        name: str,
        gender: str,
        birth_year: int,
        birth_month: int,
        birth_day: int,
        birth_hour: int,
        birth_minute: int = 0,
        calendar_type: str = "solar",
        lunar_month: int | None = None,
        lunar_day: int | None = None,
        notes: str | None = None,
        tags: list[str] | None = None,
    ) -> dict:
        """
        完整分析流程：
        1. 查找或创建用户
        2. 调用规则引擎计算
        3. 存入数据库
        4. 返回分析结果
        """
        # ── 1. 用户管理 ──
        user = self.user_repo.find_by_exact_match(name, gender, birth_year, birth_month, birth_day, birth_hour)

        if user:
            user_id = user["id"]
        else:
            tags_str = json.dumps(tags, ensure_ascii=False) if tags else None
            user_id = self.user_repo.create(
                name=name,
                gender=gender,
                birth_year=birth_year,
                birth_month=birth_month,
                birth_day=birth_day,
                birth_hour=birth_hour,
                birth_minute=birth_minute,
                calendar_type=calendar_type,
                lunar_month=lunar_month,
                lunar_day=lunar_day,
                tags=tags_str,
            )

        # ── 2. 调用规则引擎 ──
        engine_result = call_engine(
            name=name,
            gender=gender,
            year=birth_year,
            month=birth_month,
            day=birth_day,
            hour=birth_hour,
            minute=birth_minute,
            lunar_month=lunar_month,
            lunar_day=lunar_day,
        )

        if not engine_result.get("success"):
            return {
                "status": "failed",
                "error": engine_result.get("error", "引擎调用失败"),
                "user_id": user_id,
                "analysis_id": None,
            }

        # ── 3. 保存到数据库 ──
        paipan = engine_result.get("paipan", {})
        basic = engine_result.get("basic_data", {})

        # 创建分析记录
        pillars = basic.get("pillars", {})
        analysis_id = self.analysis_repo.create_analysis(
            user_id=user_id,
            bazi=paipan.get("bazi", ""),
            year_pillar=paipan.get("year_gan", "") + paipan.get("year_zhi", ""),
            month_pillar=paipan.get("month_gan", "") + paipan.get("month_zhi", ""),
            day_pillar=paipan.get("day_gan", "") + paipan.get("day_zhi", ""),
            hour_pillar=paipan.get("hour_gan", "") + paipan.get("hour_zhi", ""),
            ri_zhu=paipan.get("ri_zhu", ""),
            notes=notes,
        )

        # 保存基础数据
        pillars = basic.get("pillars", {})
        self.analysis_repo.create_basic_data(
            analysis_id=analysis_id,
            year_data=json.dumps(pillars.get("year", {}), ensure_ascii=False),
            month_data=json.dumps(pillars.get("month", {}), ensure_ascii=False),
            day_data=json.dumps(pillars.get("day", {}), ensure_ascii=False),
            hour_data=json.dumps(pillars.get("hour", {}), ensure_ascii=False),
            ri_zhu_gan=basic.get("ri_zhu", {}).get("gan", ""),
            ri_zhu_wx=basic.get("ri_zhu", {}).get("wu_xing", ""),
            ri_zhu_yy=basic.get("ri_zhu", {}).get("yin_yang", ""),
            tian_gan_notes=json.dumps(basic.get("tian_gan_notes", []), ensure_ascii=False),
            di_zhi_notes=json.dumps(basic.get("di_zhi_notes", []), ensure_ascii=False),
            cheng_gu_weight=basic.get("cheng_gu", {}).get("weight") if basic.get("cheng_gu") else None,
            cheng_gu_comment=basic.get("cheng_gu", {}).get("comment") if basic.get("cheng_gu") else None,
        )

        # 保存分析结果（新管线新增的analysis字段）
        analysis_data = engine_result.get("analysis")
        if analysis_data:
            self.analysis_repo.create_analysis_results(
                analysis_id=analysis_id,
                shen_qiang_ruo=json.dumps(analysis_data.get("shen_qiang_ruo"), ensure_ascii=False),
                cai_xing=json.dumps(analysis_data.get("cai_xing"), ensure_ascii=False),
                ge_ju=json.dumps(analysis_data.get("ge_ju"), ensure_ascii=False),
                xi_yong_shen=json.dumps(analysis_data.get("xi_yong_shen"), ensure_ascii=False),
                energy=json.dumps(analysis_data.get("energy"), ensure_ascii=False),
                da_yun=json.dumps(analysis_data.get("da_yun"), ensure_ascii=False),
                dimensions=json.dumps(analysis_data.get("dimensions"), ensure_ascii=False),
            )

        # 更新状态
        self.analysis_repo.update_status(analysis_id, "completed")

        # ── 4. 组装返回（包含完整analysis + 原始result）──
        return {
            "status": "completed",
            "analysis_id": analysis_id,
            "user_id": user_id,
            "basic": {
                "bazi": paipan.get("bazi", ""),
                "ri_zhu": basic.get("ri_zhu", {}),
                "pillars": pillars,
                "tian_gan_notes": basic.get("tian_gan_notes", []),
                "di_zhi_notes": basic.get("di_zhi_notes", []),
                "cheng_gu": basic.get("cheng_gu"),
            },
            "analysis": analysis_data,
            "result": engine_result.get("result"),
        }

    def get_analysis(self, analysis_id: int) -> dict | None:
        """获取分析结果"""
        return self.analysis_repo.get_analysis(analysis_id)

    def get_user_analyses(self, user_id: int) -> list[dict]:
        """获取用户历史分析"""
        return self.analysis_repo.get_user_analyses(user_id)
