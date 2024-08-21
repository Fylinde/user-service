# In app/routes/wishlist.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import wishlist as wishlist_schema
from app.crud import wishlist as wishlist_crud
from app.database import get_db

router = APIRouter()

@router.post("/wishlist/", response_model=wishlist_schema.WishlistRead)
def add_to_wishlist(wishlist: wishlist_schema.WishlistCreate, db: Session = Depends(get_db)):
    return wishlist_crud.add_to_wishlist(db=db, wishlist=wishlist)

@router.get("/wishlist/{user_id}", response_model=List[wishlist_schema.WishlistRead])
def get_user_wishlist(user_id: int, db: Session = Depends(get_db)):
    return wishlist_crud.get_user_wishlist(db=db, user_id=user_id)
