from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import review as review_schema
from app.crud import review as review_crud
from app.database import get_db
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
import logging

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

def verify_token(token: str):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logging.info(f"Verifying token: {token}")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logging.info(f"Token payload: {payload}")
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            logging.error("Token payload does not contain 'sub'")
            raise credentials_exception
        user_id = int(user_id_str)  # Convert user_id to integer
        return user_id
    except (JWTError, ValueError) as e:
        logging.error(f"JWTError during token validation: {e}")
        raise credentials_exception

@router.post("/", response_model=review_schema.ReviewRead)
def create_review(review: review_schema.ReviewCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = verify_token(token)
    new_review = review_crud.create_review(db, review, user_id)
    return new_review

@router.get("/products/{product_id}/reviews", response_model=List[review_schema.ReviewRead])
def get_reviews(product_id: int, db: Session = Depends(get_db)):
    reviews = review_crud.get_reviews_by_product(db, product_id)
    return reviews
