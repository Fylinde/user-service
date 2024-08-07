from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import BaseModel

class VendorModel(BaseModel):
    __tablename__ = 'vendors'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

    products = relationship("ProductModel", back_populates="vendor")
    reviews = relationship("ReviewModel", back_populates="vendor")
