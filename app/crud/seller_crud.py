from sqlalchemy.orm import Session
from app.models.seller import SellerModel
from app.schemas.seller_schemas import SellerCreate
from app.utils.rabbitmq import publish_seller_created_event, publish_user_created_event  # RabbitMQ integration for publishing messages

def create_seller(db: Session, seller: SellerCreate):
    db_seller = SellerModel(
        name=seller.name,
        description=seller.description,
        rating=seller.rating
    )
    db.add(db_seller)
    db.commit()
    db.refresh(db_seller)
    
    # Publish seller creation message to RabbitMQ for user-service to handle seller profile creation
    publish_seller_created_event(seller)
    
    return db_seller

def get_seller_by_id(db: Session, seller_id: int):
    return db.query(SellerModel).filter(SellerModel.id == seller_id).first()

def delete_seller(db: Session, seller_id: int):
    db_seller = db.query(SellerModel).filter(SellerModel.id == seller_id).first()
    if db_seller:
        db.delete(db_seller)
        db.commit()
        return True
    return False
