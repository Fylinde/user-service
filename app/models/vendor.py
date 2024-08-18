from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import BaseModel

class VendorModel(BaseModel):
    __tablename__ = 'vendors'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)  # Limit name to 100 characters
    email = Column(String(100), unique=True, index=True)  # Limit email to 100 characters
    description = Column(String(255))  # Limit description to 255 characters
    rating = Column(Integer, nullable=True)  # Optional field
    profile_picture = Column(String(255), nullable=True)  # Limit profile picture URL to 255 characters
    preferences = Column(String(255), nullable=True)  # Limit preferences JSON string to 255 characters
    hashed_password = Column(String(255))  # Ensure hashed password field is long enough for any hash

    products = relationship("ProductModel", back_populates="vendor")
    reviews = relationship("ReviewModel", back_populates="vendor")
