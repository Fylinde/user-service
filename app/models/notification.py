# app/models/notification.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import BaseModel
from datetime import datetime

class NotificationModel(BaseModel):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String(255), nullable=False)  # Notification message
    is_read = Column(Boolean, default=False)  # Track if the notification has been read
    date_created = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    seller_id = Column(Integer, ForeignKey('sellers.id'), nullable=True)  # New field for seller notifications
    user = relationship("UserModel", back_populates="notifications")
    seller = relationship("SellerModel", back_populates="notifications")

    def __repr__(self):
        return f'<Notification {self.id} - {self.message}>'
