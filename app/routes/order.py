# routes/order.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import order as order_schema
from app.crud import order as order_crud
from app.database import get_db

router = APIRouter()

@router.post("/orders/", response_model=order_schema.Order)
def create_order(order: order_schema.OrderCreate, db: Session = Depends(get_db)):
    return order_crud.create_order(db=db, order=order)

@router.get("/orders/{user_id}", response_model=List[order_schema.Order])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    return order_crud.get_orders_by_user_id(db=db, user_id=user_id)
