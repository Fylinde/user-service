# app/crud/ai_recommendation.py

from sqlalchemy.orm import Session
from app.models.ai_recommendation import AIRecommendationModel
from app.schemas.ai_recommendation import AIRecommendationCreate
from datetime import datetime

def create_ai_recommendation(db: Session, ai_recommendation: AIRecommendationCreate):
    db_recommendation = AIRecommendationModel(
        user_id=ai_recommendation.user_id,
        sellerId=ai_recommendation.sellerId,
        recommendation_data=ai_recommendation.recommendation_data,
        recommendation_type=ai_recommendation.recommendation_type,
        date_created=datetime.utcnow()
    )
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation

def get_recommendations_by_user(db: Session, user_id: str):
    return db.query(AIRecommendationModel).filter(AIRecommendationModel.user_id == user_id).all()

def get_recommendations_by_seller(db: Session, sellerId: int):
    return db.query(AIRecommendationModel).filter(AIRecommendationModel.sellerId == sellerId).all()
