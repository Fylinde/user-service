from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import BaseModel

class ReviewModel(BaseModel):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, nullable=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    rating = Column(Integer)
    comment = Column(String)

    user = relationship("UserModel", back_populates="reviews")
    vendor = relationship("VendorModel", back_populates="reviews")
