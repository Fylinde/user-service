# app/models/seller.py

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import BaseModel

class SellerModel(BaseModel):
    __tablename__ = 'sellers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)  
    email = Column(String(100), unique=True, index=True)  
    description = Column(String(255))  
    rating = Column(Integer, nullable=True)  
    profile_picture = Column(String(255), nullable=True)  
    preferences = Column(String(255), nullable=True)  
    hashed_password = Column(String(255))  
    
    # New fields
    ai_performance_score = Column(Integer, default=0)  # AI-driven performance score based on recommendation adherence
    marketplace_visibility = Column(Boolean, default=True)  # Visibility for sellers based on performance
    stock_alert_opt_in = Column(Boolean, default=True)  # Sellers can opt into stock alerts
    
    # Relationships
    #products = relationship("ProductModel", back_populates="seller")
    reviews = relationship("ReviewModel", back_populates="seller")
    recommendations = relationship("AIRecommendationModel", back_populates="seller")  # AI recommendations for sellers
    notifications = relationship("NotificationModel", back_populates="seller")
    
    
    def __repr__(self):
        return f'<Seller {self.name}>'
