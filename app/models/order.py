from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import BaseModel  # Update import path

class OrderModel(BaseModel):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    status = Column(String)
    quantity = Column(Integer)
    tracking_number = Column(String)

    user = relationship("UserModel", back_populates="orders")  # Define the user relationship
    product = relationship("ProductModel", back_populates="orders")
