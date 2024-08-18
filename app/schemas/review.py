from pydantic import BaseModel
from typing import Optional

class ReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    product_id: int
    vendor_id: int

class ReviewInDBBase(ReviewBase):
    id: int
    user_id: int
    product_id: int
    vendor_id: int

    class Config:
        from_attributes = True  # For Pydantic v2 compatibility

class ReviewRead(ReviewInDBBase):
    pass

class ReviewResponse(ReviewInDBBase):
    pass

    class Config:
        from_attributes = True  # For Pydantic v2 compatibility
