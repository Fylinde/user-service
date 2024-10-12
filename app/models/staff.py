from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import BaseModel

class StaffNotificationRecipientModel(BaseModel):
    __tablename__ = "staff_notification_recipients"

    id = Column(Integer, primary_key=True, index=True)
    staff_email = Column(String(255), unique=True, nullable=True)
    active = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserModel", back_populates="staff_notification")

