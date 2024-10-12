from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import BaseModel

class WishlistModel(BaseModel):
    __tablename__ = 'wishlists'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, nullable=True)

    user = relationship("UserModel", back_populates="wishlists")
   
