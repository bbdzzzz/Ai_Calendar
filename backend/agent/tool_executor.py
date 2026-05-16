import json
import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from backend.models.models import Event
from backend.services.event_engine import check_conflict

logger = logging.getLogger(__name__)


def execute_tool(db: Session, user_id: int, tool_name: str, arguments: dict[str, Any]) -> str:
    dispatch = {
        "query_events": _query_events,
        "create_event": _create_event,
        "update_event": _update_event,
        "delete_event": _delete_event,
    }
    handler = dispatch.get(tool_name)
    if not handler:
        return json.dumps({"status": "error", "message": f"未知工具: {tool_name}"}, ensure_ascii=False)
    try:
        result = handler(db, user_id, arguments)
        return json.dumps(result, ensure_ascii=False, default=str)
    except Exception as e:
        logger.error("工具执行异常: %s(%s) -> %s", tool_name, arguments, e)
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


def _query_events(db: Session, user_id: int, args: dict) -> dict:
    start = datetime.fromisoformat(args["start_time"])
    end = datetime.fromisoformat(args["end_time"])
    events = (
        db.query(Event)
        .filter(
            Event.user_id == user_id,
            Event.start_time < end,
            Event.end_time > start,
            Event.status != "cancelled",
        )
        .order_by(Event.start_time)
        .all()
    )
    return {
        "status": "success",
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "start_time": e.start_time.isoformat(),
                "end_time": e.end_time.isoformat(),
                "location": e.location,
                "category": e.category,
                "status": e.status,
            }
            for e in events
        ],
        "count": len(events),
    }


def _create_event(db: Session, user_id: int, args: dict) -> dict:
    start = datetime.fromisoformat(args["start_time"])
    end = datetime.fromisoformat(args["end_time"])

    conflicts = check_conflict(db, user_id, start, end)
    if conflicts:
        conflict_list = [
            f"{c.title}({c.start_time.strftime('%H:%M')}-{c.end_time.strftime('%H:%M')})"
            for c in conflicts
        ]
        return {
            "status": "conflict",
            "message": f"时间冲突，以下日程与新日程重叠: {', '.join(conflict_list)}",
            "conflicting_events": [
                {
                    "id": c.id,
                    "title": c.title,
                    "start_time": c.start_time.isoformat(),
                    "end_time": c.end_time.isoformat(),
                }
                for c in conflicts
            ],
        }

    event = Event(
        user_id=user_id,
        title=args["title"],
        start_time=start,
        end_time=end,
        location=args.get("location"),
        category=args.get("category", "other"),
        priority=args.get("priority", "medium"),
        description=args.get("description"),
        status="confirmed",
        source="ai",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return {
        "status": "success",
        "message": "日程创建成功",
        "event": {
            "id": event.id,
            "title": event.title,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "location": event.location,
            "category": event.category,
            "status": event.status,
        },
    }


def _update_event(db: Session, user_id: int, args: dict) -> dict:
    event_id = args["event_id"]
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == user_id).first()
    if not event:
        return {"status": "error", "message": f"日程ID {event_id} 不存在"}

    if "start_time" in args or "end_time" in args:
        new_start = datetime.fromisoformat(args["start_time"]) if "start_time" in args else event.start_time
        new_end = datetime.fromisoformat(args["end_time"]) if "end_time" in args else event.end_time
        conflicts = check_conflict(db, user_id, new_start, new_end, exclude_id=event_id)
        if conflicts:
            conflict_list = [
                f"{c.title}({c.start_time.strftime('%H:%M')}-{c.end_time.strftime('%H:%M')})"
                for c in conflicts
            ]
            return {
                "status": "conflict",
                "message": f"时间冲突: {', '.join(conflict_list)}",
                "conflicting_events": [
                    {
                        "id": c.id,
                        "title": c.title,
                        "start_time": c.start_time.isoformat(),
                        "end_time": c.end_time.isoformat(),
                    }
                    for c in conflicts
                ],
            }

    updatable = ["title", "start_time", "end_time", "location", "category", "priority", "status", "description"]
    for key in updatable:
        if key in args:
            val = args[key]
            if key in ("start_time", "end_time") and isinstance(val, str):
                val = datetime.fromisoformat(val)
            setattr(event, key, val)
    db.commit()
    db.refresh(event)
    return {
        "status": "success",
        "message": "日程更新成功",
        "event": {
            "id": event.id,
            "title": event.title,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "location": event.location,
            "category": event.category,
            "status": event.status,
        },
    }


def _delete_event(db: Session, user_id: int, args: dict) -> dict:
    event_id = args["event_id"]
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == user_id).first()
    if not event:
        return {"status": "error", "message": f"日程ID {event_id} 不存在"}
    event.status = "cancelled"
    db.commit()
    return {"status": "success", "message": f"日程'{event.title}'已删除"}
