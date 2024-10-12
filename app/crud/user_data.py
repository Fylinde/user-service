from sqlalchemy.orm import Session
from app.models.user_data import UserDataModel

def create_user_data(db: Session, user_data: UserDataModel):
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return user_data

def get_user_data(db: Session, user_id: int):
    return db.query(UserDataModel).filter(UserDataModel.user_id == user_id).first()
