from typing import Optional

from pydantic import BaseModel, Field


class AgentInput(BaseModel):
    user_id: int
    current_query: str
    conversation_history: list[dict] = Field(default_factory=list)
    current_context: dict = Field(default_factory=dict)


class AgentAction(BaseModel):
    action_type: str = "text_reply"
    text_response: str = ""
    event_data: Optional[dict] = None
    new_messages: list[dict] = Field(default_factory=list)
