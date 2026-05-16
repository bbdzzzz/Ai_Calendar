from datetime import date, datetime

from pydantic import BaseModel


class ReportOut(BaseModel):
    id: int
    user_id: int
    report_type: str
    start_date: date
    end_date: date
    summary: str | None = None
    statistics: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportQuery(BaseModel):
    report_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None
