# schemas/order.py
from pydantic import BaseModel
from typing import Optional

class OrderBase(BaseModel):
    status: str
    tracking_number: Optional[str] = None

class OrderCreate(OrderBase):
    user_id: int
    product_id: int
    quantity: int

class OrderInDBBase(OrderBase):
    id: int
    user_id: int
    product_id: int

    class Config:
        from_attributes = True  # Update this line for Pydantic v2

class Order(OrderInDBBase):
    pass
