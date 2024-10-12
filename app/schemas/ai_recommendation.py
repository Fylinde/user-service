# app/schemas/ai_recommendation.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AIRecommendationBase(BaseModel):
    recommendation_type: str  # Stocking recommendation, pricing, visibility, etc.
    recommendation_data: dict  # JSON containing the actual recommendation details

class AIRecommendationCreate(AIRecommendationBase):
    user_id: int
    vendor_id: int

class AIRecommendationResponse(AIRecommendationBase):
    id: int
    date_created: datetime

    class Config:
        orm_mode = True
        from_attributes = True
