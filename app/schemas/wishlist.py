from pydantic import BaseModel
from typing import Optional

class WishlistBase(BaseModel):
    product_id: int
    user_id: int

class WishlistCreate(WishlistBase):
    pass

class WishlistInDBBase(WishlistBase):
    id: int

    class Config:
        orm_mode = True  # This was changed to orm_mode as Pydantic v2 is compatible with this.

class WishlistRead(WishlistInDBBase):
    pass
