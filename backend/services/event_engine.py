from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.models import Event


def check_conflict(db: Session, user_id: int, start_time: datetime, end_time: datetime, exclude_id: int | None = None) -> list[Event]:
    q = db.query(Event).filter(
        Event.user_id == user_id,
        Event.start_time < end_time,
        Event.end_time > start_time,
        Event.status != "cancelled",
    )
    if exclude_id:
        q = q.filter(Event.id != exclude_id)
    return q.all()
