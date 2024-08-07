from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import BaseModel

class ProductModel(BaseModel):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    vendor_id = Column(Integer, ForeignKey('vendors.id'))

    reviews = relationship("ReviewModel", back_populates="product")
    orders = relationship("OrderModel", back_populates="product")
    wishlists = relationship("WishlistModel", back_populates="product")
    vendor = relationship("VendorModel", back_populates="products")
