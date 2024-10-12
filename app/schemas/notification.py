# app/schemas/notification.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationBase(BaseModel):
    message: str
    is_read: bool = False

class NotificationResponse(NotificationBase):
    id: int
    date_created: datetime
    user_id: Optional[int]
    vendor_id: Optional[int]

    class Config:
        orm_mode = True
        from_attributes = True

class NotificationCreate(NotificationBase):
    user_id: int

