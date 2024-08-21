from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from app.schemas.product import ProductResponse
from app.schemas.review import ReviewResponse

class VendorBase(BaseModel):
    name: str = Field(..., example="Acme Corp")
    email: EmailStr = Field(..., example="contact@acmecorp.com")
    description: Optional[str] = Field(None, example="Leading provider of quality goods")
    rating: Optional[int] = Field(None, example=5)
    profile_picture: Optional[str] = Field(None, example="https://example.com/profile.jpg")
    preferences: Optional[str] = Field(None, example="{'theme': 'dark'}")

class VendorCreate(VendorBase):
    password: str = Field(..., example="securepassword123")

class VendorUpdate(VendorBase):
    password: Optional[str] = None

class VendorResponse(VendorBase):
    id: int
    name: str
    description: Optional[str] = None
    rating: Optional[float] = None

    class Config:
        orm_mode = True

class VendorWithDetails(VendorResponse):
    products: List[ProductResponse] = []
    reviews: List[ReviewResponse] = []


