from sqlalchemy.orm import Session
from app.models.wishlist import WishlistModel
from app.schemas import wishlist as wishlist_schema

def add_to_wishlist(db: Session, wishlist: wishlist_schema.WishlistCreate):
    db_wishlist = WishlistModel(**wishlist.dict())
    db.add(db_wishlist)
    db.commit()
    db.refresh(db_wishlist)
    return db_wishlist

def get_user_wishlist(db: Session, user_id: int):
    return db.query(WishlistModel).filter(WishlistModel.user_id == user_id).all()
