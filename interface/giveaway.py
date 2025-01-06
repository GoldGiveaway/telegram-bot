from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

class IChannel(BaseModel):
    id: int
    message_id: Optional[int]
    link: str
    name: str
    photo: Optional[str]

class IMember(BaseModel):
    id: int
    date: datetime

class IGiveaway(BaseModel):
    giveaway_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_et: datetime
    title: str
    owner_id: int
    description: str = ''
    win_count: int = 1
    channels: List[IChannel] = Field(default_factory=list)
    members: List[IMember] = Field(default_factory=list)
    last_message_update: Optional[datetime] = None
    status: Literal["active", "wait", "finalized"] = 'wait'
    winners: Optional[List[int]] = Field(default_factory=list)
