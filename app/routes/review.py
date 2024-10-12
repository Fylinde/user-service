# routes/review.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import review as review_schema
from app.crud import review as review_crud, vendor as vendor_crud
from app.database import get_db
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
import logging
from app.crud.notification import create_notification, get_notifications_by_user, get_notifications_by_vendor
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
        user_id = int(user_id_str)
        return user_id
    except (JWTError, ValueError) as e:
        logging.error(f"JWTError during token validation: {e}")
        raise credentials_exception
# routes/review.py

@router.post("/", response_model=review_schema.ReviewRead)
def create_review(review: review_schema.ReviewCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = verify_token(token)
    new_review = review_crud.create_review(db, review, user_id)

    # Update the vendor's performance score after each review
    vendor_id = review.vendor_id
    performance_score = calculate_performance_score(review.rating)
    vendor_crud.update_vendor_performance_score(db, vendor_id, performance_score)

    # Notify vendor about the new review
    message = f"New review for your product with rating {review.rating}."
    create_notification(db, message=message, vendor_id=vendor_id)

    logging.info(f"Notified vendor {vendor_id} about new review.")
    return new_review


@router.get("/products/{product_id}/reviews", response_model=List[review_schema.ReviewRead])
def get_reviews(product_id: int, db: Session = Depends(get_db)):
    reviews = review_crud.get_reviews_by_product(db, product_id)
    return reviews

def calculate_performance_score(rating: int) -> int:
    """Simple calculation of performance score based on rating."""
    if rating >= 4:
        return 10  # Increase score by 10 for good ratings
    elif rating == 3:
        return 5   # Average ratings increase score by 5
    else:
        return -10  # Decrease score for bad reviews
