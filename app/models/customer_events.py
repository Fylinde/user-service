from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.database import BaseModel
from datetime import datetime

class CustomerEventModel(BaseModel):
    __tablename__ = "customer_events"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(255), nullable=False)
    parameters = Column(JSONB, default=dict)
    date = Column(DateTime, default=datetime.utcnow)

    customer_id = Column(Integer, ForeignKey("users.id"))
    customer = relationship("UserModel", back_populates="events")


