from typing import Optional

from pydantic import BaseModel


class AgentInput(BaseModel):
    user_id: int
    current_query: str
    conversation_history: list[dict]
    current_context: dict


class AgentAction(BaseModel):
    action_type: str
    text_response: str
    event_data: Optional[dict] = None
