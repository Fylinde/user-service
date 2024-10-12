from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import BaseModel

class UserDataModel(BaseModel):
    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    search_history = Column(String, nullable=True)  # JSON string to track search queries
    interactions = Column(String, nullable=True)  # Track product/category interactions
    recently_viewed = Column(String, nullable=True)  # Store recently viewed products
    category_preferences = Column(String, nullable=True)  # Preferences for personalized categories

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Potential future fields for enhancing personalization
    purchase_history = Column(String, nullable=True)  # To track past purchases for category recommendations
    wishlist = Column(String, nullable=True)  # Track user wishlists for analysis
