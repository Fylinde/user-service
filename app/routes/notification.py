# routes/notification.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.notification import NotificationResponse
from app.crud import notification as notification_crud
from app.database import get_db
from typing import List
router = APIRouter()

@router.get("/vendor/{vendor_id}/notifications", response_model=List[NotificationResponse])
def get_vendor_notifications(vendor_id: int, db: Session = Depends(get_db)):
    """Retrieve all notifications for a vendor."""
    return notification_crud.get_notifications_by_vendor(db=db, vendor_id=vendor_id)

@router.post("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(notification_id: int, db: Session = Depends(get_db)):
    """Mark a notification as read."""
    return notification_crud.mark_notification_as_read(db=db, notification_id=notification_id)
