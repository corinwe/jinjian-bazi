"""金鉴真人·分析历史管理路由 v1.0 — 保存/查询分析历史"""

from fastapi import APIRouter, Depends, HTTPException

from api.routers.auth import get_current_user
from database.connection import get_connection, row_to_dict, rows_to_dicts

router = APIRouter(prefix="/api/v1", tags=["analyses"])


@router.post("/analyses")
async def save_analysis(data: dict, user: dict = Depends(get_current_user)):
    """保存分析结果到历史"""
    conn = get_connection()
    try:
        # Extract basic info from _meta
        meta = data.get("_meta", {})
        bazi = data.get("paipan", {}).get("bazi", "") or data.get("result", {}).get("sec_1_overview", {}).get(
            "bazi", ""
        )
        pillars = data.get("basic_data", {}).get("pillars", {})

        conn.execute(
            """
            INSERT INTO analyses (user_id, bazi, year_pillar, month_pillar, day_pillar, hour_pillar, ri_zhu, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'completed')
        """,
            (
                user["user_id"],
                bazi,
                pillars.get("year", {}).get("tian_gan", "") + (pillars.get("year", {}).get("di_zhi", "") or ""),
                pillars.get("month", {}).get("tian_gan", "") + (pillars.get("month", {}).get("di_zhi", "") or ""),
                pillars.get("day", {}).get("tian_gan", "") + (pillars.get("day", {}).get("di_zhi", "") or ""),
                pillars.get("hour", {}).get("tian_gan", "") + (pillars.get("hour", {}).get("di_zhi", "") or ""),
                data.get("basic_data", {}).get("ri_zhu", {}).get("gan", "") or "",
            ),
        )
        conn.commit()
        return {"success": True, "message": "保存成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {e}")
    finally:
        conn.close()


@router.get("/analyses")
async def get_history(user: dict = Depends(get_current_user)):
    """获取当前用户的历史分析记录"""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT id, bazi, ri_zhu, status, created_at
            FROM analyses
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 50
        """,
            (user["user_id"],),
        )
        rows = rows_to_dicts(cursor.fetchall())

        # Get name from the stored data if available
        results = []
        for row in rows:
            results.append(
                {
                    "id": row["id"],
                    "bazi": row["bazi"],
                    "ri_zhu": row["ri_zhu"],
                    "status": row["status"],
                    "created_at": row["created_at"],
                    "name": f"分析 #{row['id']}",
                }
            )

        return {"success": True, "analyses": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {e}")
    finally:
        conn.close()


@router.get("/analyses/{analysis_id}")
async def get_analysis_detail(analysis_id: int, user: dict = Depends(get_current_user)):
    """获取单个分析详情（含引擎完整结果）"""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, bazi, status, created_at FROM analyses WHERE id = ? AND user_id = ?",
            (analysis_id, user["user_id"]),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="分析记录不存在")

        return {"success": True, "analysis": row_to_dict(row)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {e}")
    finally:
        conn.close()
