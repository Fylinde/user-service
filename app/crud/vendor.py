# app/crud/vendor.py

from sqlalchemy.orm import Session
from app.models.vendor import VendorModel
from app.schemas.vendor import VendorCreate, VendorUpdate

def create_vendor(db: Session, vendor: VendorCreate):
    """Create a vendor profile in user-service."""
    db_vendor = VendorModel(
        name=vendor.name,
        description=vendor.description,
        rating=vendor.rating,
        ai_performance_score=0,  # New field initialized to 0
        marketplace_visibility=True,  # New field
        stock_alert_opt_in=True  # New field
    )
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

def get_vendor_by_id(db: Session, vendor_id: int):
    return db.query(VendorModel).filter(VendorModel.id == vendor_id).first()

def update_vendor(db: Session, db_vendor: VendorModel, vendor_update: VendorUpdate):
    vendor_data = vendor_update.dict(exclude_unset=True)
    for key, value in vendor_data.items():
        setattr(db_vendor, key, value)
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

def delete_vendor(db: Session, vendor_id: int):
    db_vendor = db.query(VendorModel).filter(VendorModel.id == vendor_id).first()
    if db_vendor:
        db.delete(db_vendor)
        db.commit()
        return True
    return False

# New function to update vendor's AI performance score
def update_vendor_performance_score(db: Session, vendor_id: int, score: int):
    db_vendor = db.query(VendorModel).filter(VendorModel.id == vendor_id).first()
    if db_vendor:
        db_vendor.ai_performance_score += score
        db.add(db_vendor)
        db.commit()
        return db_vendor
    return None
