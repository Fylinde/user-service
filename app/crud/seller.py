# app/crud/seller.py

from sqlalchemy.orm import Session
from app.models.seller import SellerModel
from app.schemas.seller import SellerCreate, SellerUpdate

def create_seller(db: Session, seller: SellerCreate):
    """Create a seller profile in user-service."""
    db_seller = SellerModel(
        name=seller.name,
        description=seller.description,
        rating=seller.rating,
        ai_performance_score=0,  # New field initialized to 0
        marketplace_visibility=True,  # New field
        stock_alert_opt_in=True  # New field
    )
    db.add(db_seller)
    db.commit()
    db.refresh(db_seller)
    return db_seller

def get_seller_by_id(db: Session, seller_id: int):
    return db.query(SellerModel).filter(SellerModel.id == seller_id).first()

def update_seller(db: Session, db_seller: SellerModel, Seller_update: SellerUpdate):
    seller_data = Seller_update.dict(exclude_unset=True)
    for key, value in seller_data.items():
        setattr(db_seller, key, value)
    db.add(db_seller)
    db.commit()
    db.refresh(db_seller)
    return db_seller

def delete_seller(db: Session, seller_id: int):
    db_seller = db.query(SellerModel).filter(SellerModel.id == seller_id).first()
    if db_seller:
        db.delete(db_seller)
        db.commit()
        return True
    return False

# New function to update seller's AI performance score
def update_seller_performance_score(db: Session, seller_id: int, score: int):
    db_seller = db.query(SellerModel).filter(SellerModel.id == seller_id).first()
    if db_seller:
        db_seller.ai_performance_score += score
        db.add(db_seller)
        db.commit()
        return db_seller
    return None
