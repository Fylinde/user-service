from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_data import UserDataModel
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()
@router.post("/user_data/", response_model=UserResponse)
def save_user_data(user_data: UserCreate, db: Session = Depends(get_db)):
    # Validate the user_id with user-service if needed
    db_user_data = UserDataModel(**user_data.dict())
    db.add(db_user_data)
    db.commit()
    db.refresh(db_user_data)
    return db_user_data
