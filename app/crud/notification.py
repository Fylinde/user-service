# app/crud/notification.py

from sqlalchemy.orm import Session
from app.models.notification import NotificationModel
from datetime import datetime

def create_notification(db: Session, message: str, user_id: str = None, sellerId: str = None):
    """Create a notification for a user or a seller."""
    db_notification = NotificationModel(
        user_id=user_id,
        sellerId=sellerId,
        message=message,
        is_read=False,
        date_created=datetime.utcnow()
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notifications_by_user(db: Session, user_id: str):
    return db.query(NotificationModel).filter(NotificationModel.user_id == user_id).all()

def get_notifications_by_seller(db: Session, sellerId: int):
    return db.query(NotificationModel).filter(NotificationModel.sellerId == sellerId).all()

def mark_notification_as_read(db: Session, notification_id: int):
    db_notification = db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
    if db_notification:
        db_notification.is_read = True
        db.add(db_notification)
        db.commit()
        return db_notification
    return None
