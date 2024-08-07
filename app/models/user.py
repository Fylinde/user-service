from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import BaseModel
from datetime import datetime

class UserModel(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    profile_picture = Column(String, nullable=True)
    preferences = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True)
    password_last_updated = Column(DateTime, default=datetime.utcnow)
    failed_login_attempts = Column(Integer, default=0)
    account_locked = Column(Boolean, default=False)
    backup_codes = Column(String, nullable=True)

    reviews = relationship("ReviewModel", back_populates="user")
    orders = relationship("OrderModel", back_populates="user")
    wishlists = relationship("WishlistModel", back_populates="user")
