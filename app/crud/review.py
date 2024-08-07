from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.models.review import ReviewModel
from app.schemas.review import ReviewCreate

def create_review(db: Session, review: ReviewCreate, user_id: int):
    db_review = ReviewModel(**review.dict(), user_id=user_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_reviews_by_product(db: Session, product_id: int):
    result = db.execute(select(ReviewModel).filter(ReviewModel.product_id == product_id))
    return result.scalars().all()
