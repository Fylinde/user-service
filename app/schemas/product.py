from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.review import ReviewResponse
from app.schemas.order import OrderResponse
from app.schemas.wishlist import WishlistResponse

class ProductBase(BaseModel):
    name: str = Field(..., example="Product Name")
    description: Optional[str] = Field(None, example="This is a great product.")
    price: float = Field(..., example=99.99)

class ProductCreate(ProductBase):
    vendor_id: int = Field(..., example=1)

class ProductUpdate(ProductBase):
    vendor_id: Optional[int] = None

class ProductResponse(ProductBase):
    id: int

    class Config:
        orm_mode = True

class ProductWithDetails(ProductResponse):
    reviews: List[ReviewResponse] = []
    orders: List[OrderResponse] = []
    wishlists: List[WishlistResponse] = []
