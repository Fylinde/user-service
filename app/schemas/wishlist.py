from pydantic import BaseModel

class WishlistBase(BaseModel):
    product_id: int
    user_id: int

class WishlistCreate(WishlistBase):
    pass

class WishlistInDBBase(WishlistBase):
    id: int

    class Config:
        from_attributes = True  # For Pydantic v2 compatibility

class WishlistRead(WishlistInDBBase):
    pass

class WishlistResponse(WishlistInDBBase):
    pass

    class Config:
        from_attributes = True  # For Pydantic v2 compatibility
