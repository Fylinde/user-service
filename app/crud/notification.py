# app/crud/notification.py

from sqlalchemy.orm import Session
from app.models.notification import NotificationModel
from datetime import datetime

def create_notification(db: Session, message: str, user_id: int = None, vendor_id: int = None):
    """Create a notification for a user or a vendor."""
    db_notification = NotificationModel(
        user_id=user_id,
        vendor_id=vendor_id,
        message=message,
        is_read=False,
        date_created=datetime.utcnow()
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notifications_by_user(db: Session, user_id: int):
    return db.query(NotificationModel).filter(NotificationModel.user_id == user_id).all()

def get_notifications_by_vendor(db: Session, vendor_id: int):
    return db.query(NotificationModel).filter(NotificationModel.vendor_id == vendor_id).all()

def mark_notification_as_read(db: Session, notification_id: int):
    db_notification = db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
    if db_notification:
        db_notification.is_read = True
        db.add(db_notification)
        db.commit()
        return db_notification
    return None
