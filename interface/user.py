from typing import Optional
from datetime import datetime, UTC
from pydantic import BaseModel, Field

class IUser(BaseModel):
    user_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    username: Optional[str]
    last_name: Optional[str]
    first_name: Optional[str]
