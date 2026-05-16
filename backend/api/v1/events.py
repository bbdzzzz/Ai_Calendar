from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user
from backend.core.database import get_db
from backend.models.models import Event, User
from backend.schemas.event import EventCreate, EventOut, EventUpdate

router = APIRouter(prefix="/events", tags=["行程"])


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(body: EventCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if body.start_time >= body.end_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="开始时间必须早于结束时间")
    event = Event(user_id=current_user.id, **body.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=list[EventOut])
def list_events(
    start: datetime | None = Query(None, description="筛选起始时间"),
    end: datetime | None = Query(None, description="筛选结束时间"),
    category: str | None = Query(None),
    status: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Event).filter(Event.user_id == current_user.id)
    if start:
        q = q.filter(Event.end_time > start)
    if end:
        q = q.filter(Event.start_time < end)
    if category:
        q = q.filter(Event.category == category)
    if status:
        q = q.filter(Event.status == status)
    return q.order_by(Event.start_time).all()


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="行程不存在")
    return event


@router.put("/{event_id}", response_model=EventOut)
def update_event(
    event_id: int, body: EventUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="行程不存在")
    update_data = body.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(event, k, v)
    if event.start_time >= event.end_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="开始时间必须早于结束时间")
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="行程不存在")
    db.delete(event)
    db.commit()
