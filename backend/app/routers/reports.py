"""报告路由: 查询/管理"""

import json

from app.auth import require_user
from app.database import get_db
from app.models import Report, ReportVersion
from app.schemas import ReportListResponse, ReportResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

router = APIRouter(prefix="/reports", tags=["报告"])


@router.get("", response_model=ReportListResponse)
def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    user=Depends(require_user),
    db: Session = Depends(get_db),
):
    """获取我的报告列表"""
    query = db.query(Report).filter(Report.user_id == user.id)
    total = query.count()
    items = query.order_by(desc(Report.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    return ReportListResponse(
        total=total,
        items=[
            ReportResponse(
                id=r.id,
                bazi=r.bazi_str,
                gender=r.gender,
                version=r.version,
                result=json.loads(r.result_json) if r.result_json else None,
                created_at=r.created_at,
            )
            for r in items
        ],
    )


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, user=Depends(require_user), db: Session = Depends(get_db)):
    """获取单份报告"""
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == user.id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在或无权限")

    return ReportResponse(
        id=report.id,
        bazi=report.bazi_str,
        gender=report.gender,
        version=report.version,
        result=json.loads(report.result_json) if report.result_json else None,
        created_at=report.created_at,
    )


@router.get("/{report_id}/versions")
def get_report_versions(report_id: int, user=Depends(require_user), db: Session = Depends(get_db)):
    """获取报告版本历史"""
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == user.id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    versions = (
        db.query(ReportVersion)
        .filter(ReportVersion.report_id == report_id)
        .order_by(desc(ReportVersion.created_at))
        .all()
    )

    return [
        {
            "version": v.version,
            "changelog": v.changelog,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }
        for v in versions
    ]
