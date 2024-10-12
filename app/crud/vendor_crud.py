from sqlalchemy.orm import Session
from app.models.vendor import VendorModel
from app.schemas.vendor_schemas import VendorCreate
from app.utils.rabbitmq import publish_vendor_created_event, publish_user_created_event  # RabbitMQ integration for publishing messages

def create_vendor(db: Session, vendor: VendorCreate):
    db_vendor = VendorModel(
        name=vendor.name,
        description=vendor.description,
        rating=vendor.rating
    )
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    
    # Publish vendor creation message to RabbitMQ for user-service to handle vendor profile creation
    publish_vendor_created_event(vendor)
    
    return db_vendor

def get_vendor_by_id(db: Session, vendor_id: int):
    return db.query(VendorModel).filter(VendorModel.id == vendor_id).first()

def delete_vendor(db: Session, vendor_id: int):
    db_vendor = db.query(VendorModel).filter(VendorModel.id == vendor_id).first()
    if db_vendor:
        db.delete(db_vendor)
        db.commit()
        return True
    return False
