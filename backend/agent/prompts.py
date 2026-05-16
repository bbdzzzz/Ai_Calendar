import json
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.models.models import Conversation, Event
from backend.schemas.agent import AgentInput

logger = logging.getLogger(__name__)


def build_agent_input(db: Session, user_id: int, query: str) -> AgentInput:
    history_records = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
        .limit(20)
        .all()
    )
    conversation_history = [{"role": r.role, "content": r.content} for r in reversed(history_records)]

    now = datetime.now()
    upcoming_events = (
        db.query(Event)
        .filter(Event.user_id == user_id, Event.start_time >= now, Event.start_time < now + timedelta(days=7))
        .order_by(Event.start_time)
        .limit(10)
        .all()
    )

    current_context = {
        "time": now.isoformat(),
        "events": [
            {
                "title": e.title,
                "start_time": e.start_time.isoformat(),
                "end_time": e.end_time.isoformat(),
                "status": e.status,
            }
            for e in upcoming_events
        ],
    }

    return AgentInput(
        user_id=user_id,
        current_query=query,
        conversation_history=conversation_history,
        current_context=current_context,
    )
