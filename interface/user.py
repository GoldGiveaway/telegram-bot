from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class IUser(BaseModel):
    user_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    username: Optional[str]
    last_name: Optional[str]
    first_name: Optional[str]
