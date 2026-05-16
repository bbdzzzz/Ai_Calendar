from datetime import datetime

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = None
    start_time: datetime
    end_time: datetime
    location: str | None = None
    category: str = "other"
    priority: str = "medium"
    status: str = "confirmed"
    source: str = "manual"


class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    location: str | None = None
    category: str | None = None
    priority: str | None = None
    status: str | None = None


class EventOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime
    location: str | None = None
    category: str
    priority: str
    status: str
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EventUpsertWS(BaseModel):
    temp_id: str
    title: str
    start_time: datetime
    end_time: datetime
    location: str | None = None
    category: str = "other"
    priority: str = "medium"
    status: str = "tentative"
    description: str | None = None


class EventConfirmWS(BaseModel):
    temp_id: str
    confirmed: bool
