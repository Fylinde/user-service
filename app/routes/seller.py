from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.seller import SellerModel
from app.schemas.token import Token
from app.schemas.seller_schemas import SellerResponse, SellerCreate
from app.security import TokenData, verify_password, create_access_token, get_password_hash
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.seller_schemas import SellerLogin
import logging
import pika
import json
from app.security import pwd_context
from app.utils.rabbitmq import publish_seller_created_event

logger = logging.getLogger("auth_service")
logging.basicConfig(level=logging.INFO)
router = APIRouter()

@router.post("/register_seller", response_model=SellerResponse)
def register_seller(seller: SellerCreate, db: Session = Depends(get_db)):
    # Check if the Seller already exists
    existing_seller = db.query(SellerModel).filter(SellerModel.email == seller.email).first()
    if existing_seller:
        raise HTTPException(status_code=400, detail="seller with this email already registered")

    # Create the seller
    seller_obj = SellerModel(
        name=seller.name,
        email=seller.email,
        description=seller.description,
        rating=seller.rating,
        profile_picture=seller.profile_picture,
        preferences=seller.preferences,
        hashed_password=pwd_context.hash(seller.password),
    )
    db.add(seller_obj)
    db.commit()
    db.refresh(seller_obj)

    # Log seller creation
    logger.info(f"seller created in auth-service: {seller_obj.name} (ID: {seller_obj.id})")

    # Prepare seller data to publish
    seller_data = {
        "id": seller_obj.id,
        "name": seller_obj.name,
        "email": seller_obj.email,
        "description": seller_obj.description,
        "rating": seller_obj.rating,
        "profile_picture": seller_obj.profile_picture,
        "preferences": seller_obj.preferences,
        "hashed_password": seller_obj.hashed_password,
    }
    publish_seller_created_event(seller_data)

    return seller_obj

@router.post("/login")
def seller_login(credentials: SellerLogin, db: Session = Depends(get_db)):
    db_seller = db.query(SellerModel).filter(SellerModel.email == credentials.email).first()
    if not db_seller or not verify_password(credentials.password, db_seller.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(data={"user_id": db_seller.id, "is_admin": False})  # Assuming sellers aren't admins
    return {"access_token": token, "token_type": "bearer"}
