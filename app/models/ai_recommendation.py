# app/models/ai_recommendation.py

from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.database import BaseModel
from datetime import datetime

class AIRecommendationModel(BaseModel):
    __tablename__ = "ai_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_data = Column(JSON, nullable=False)  # Stores recommendation data (e.g., stock, fulfillment suggestions)
    date_created = Column(DateTime, default=datetime.utcnow)
    recommendation_type = Column(String(100))  # Type of recommendation (stock, visibility, pricing, etc.)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserModel", back_populates="ai_recommendations")
    
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    vendor = relationship("VendorModel", back_populates="recommendations")
    
    def __repr__(self):
        return f'<AIRecommendation {self.id} - {self.recommendation_type}>'
