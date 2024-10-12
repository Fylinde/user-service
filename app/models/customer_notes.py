from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import BaseModel
from datetime import datetime

class CustomerNoteModel(BaseModel):
    __tablename__ = "customer_notes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    is_public = Column(Boolean, default=True)

    customer_id = Column(Integer, ForeignKey("users.id"))
    customer = relationship("UserModel", back_populates="notes")

