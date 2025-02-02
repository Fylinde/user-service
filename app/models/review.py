from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import BaseModel

class ReviewModel(BaseModel):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, nullable=True)
    seller_id = Column(Integer, ForeignKey('sellers.id'))
    rating = Column(Integer)
    comment = Column(String)

    user = relationship("UserModel", back_populates="reviews")
    seller = relationship("SellerModel", back_populates="reviews")
