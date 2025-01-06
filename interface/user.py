from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from services import date

class IUser(BaseModel):
    user_id: int
    created_at: datetime = Field(default_factory=date.now_datetime)
    username: Optional[str]
    last_name: Optional[str]
    first_name: Optional[str]
