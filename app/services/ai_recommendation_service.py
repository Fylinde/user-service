# app/services/ai_recommendation_service.py

from sqlalchemy.orm import Session
from app.crud import notification as notification_crud
import logging

def generate_ai_recommendations_for_vendor(db_session: Session, vendor_id: int):
    """
    Generate AI-based recommendations for a vendor and notify the vendor.
    """
    # Placeholder for AI recommendation logic. You can expand this to include
    # more advanced logic like ML models, sales analysis, etc.
    recommendation_type = "Stock Optimization"
    
    # Assuming you create AI recommendations here
    recommendation_data = {
        "optimal_stock": 50,  # Example data for optimal stock level
        "recommended_warehouse": "Warehouse A"
    }

    # Notify vendor about the AI recommendation
    notify_ai_recommendation(db_session, vendor_id, recommendation_type)

    logging.info(f"Generated AI recommendation for Vendor {vendor_id}: {recommendation_data}")

def notify_ai_recommendation(db_session: Session, vendor_id: int, recommendation_type: str):
    """
    Notify the vendor about a new AI recommendation.
    """
    message = f"You have a new AI recommendation: {recommendation_type}."
    notification_crud.create_notification(db_session, message=message, vendor_id=vendor_id)
    
    logging.info(f"AI recommendation notification sent to Vendor {vendor_id}")

