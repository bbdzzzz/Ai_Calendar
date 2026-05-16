from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user
from backend.core.database import get_db
from backend.models.models import Report, User
from backend.schemas.report import ReportOut

router = APIRouter(prefix="/reports", tags=["报告"])


@router.get("", response_model=list[ReportOut])
def list_reports(
    report_type: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Report).filter(Report.user_id == current_user.id)
    if report_type:
        q = q.filter(Report.report_type == report_type)
    return q.order_by(Report.created_at.desc()).all()


@router.get("/{report_id}", response_model=ReportOut)
def get_report(report_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == current_user.id).first()
    if not report:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报告不存在")
    return report
