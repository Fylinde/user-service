# app/crud/user.py

from sqlalchemy.orm import Session
from app.models.user import UserModel
from app.schemas.user import UserCreate, UserUpdate
from app.models.notification import NotificationModel
from app.models.ai_recommendation import AIRecommendationModel
from datetime import datetime, timedelta
from app.utils.rabbitmq import RabbitMQConnection  # RabbitMQ integration for publishing messages
from fastapi import HTTPException
from app.services.usermanager import UserManager
from app.utils.password_utils import get_password_hash 
import logging
from sqlalchemy.exc import IntegrityError
from app.utils.code_generator import generate_verification_code
from passlib.context import CryptContext
# Set up logging
logger = logging.getLogger("user_service")

logging.basicConfig(level=logging.INFO)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(UserModel).offset(skip).limit(limit).all()

def update_user(db: Session, db_user: UserModel, user_update: UserUpdate):
    user_data = user_update.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# New function to create a notification
def create_notification(db: Session, user_id: int, message: str):
    db_notification = NotificationModel(
        user_id=user_id,
        message=message,
        is_read=False,
        date_created=datetime.utcnow()
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

# New function to get notifications for a user
def get_notifications_by_user(db: Session, user_id: int):
    return db.query(NotificationModel).filter(NotificationModel.user_id == user_id).all()

# New function to create AI recommendations for a user
def create_ai_recommendation(db: Session, user_id: int, vendor_id: int, recommendation_data: dict, recommendation_type: str):
    db_recommendation = AIRecommendationModel(
        user_id=user_id,
        vendor_id=vendor_id,
        recommendation_data=recommendation_data,
        recommendation_type=recommendation_type,
        date_created=datetime.utcnow()
    )
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation

# Get AI recommendations for a user
def get_ai_recommendations_by_user(db: Session, user_id: int):
    return db.query(AIRecommendationModel).filter(AIRecommendationModel.user_id == user_id).all()


def create_admin(db: Session, user: UserCreate):
    """Create an admin user using the UserManager."""
    hashed_password = get_password_hash(user.password)  # Assumes the password is provided and needs hashing
    db_user = UserManager.create_user(
        session=db,
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone_number,
        profile_picture=user.profile_picture,
        preferences=user.preferences,
        is_staff=False  # Regular users are not staff by default
    )
    
    # No need to publish or send emails; this is now handled by auth-service
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    """Retrieve a user by their email."""
    return db.query(UserModel).filter(UserModel.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    """Retrieve a user by their ID."""
    return db.query(UserModel).filter(UserModel.id == user_id).first()



def delete_user(db: Session, user_id: int):
    """Delete a user by their ID."""
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

def get_user_by_code(db: Session, code: str):
    user = db.query(UserModel).filter(UserModel.verification_code == code).first()
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    # You can add checks for admin users here if necessary
    if user.is_admin:
        logger.info(f"Admin user {user.full_name} verified")
    else:
        logger.info(f"Regular user {user.full_name} verified")
    
    return user

def get_user_by_verification_code(db: Session, code: str) -> UserModel:
    """Fetch the user by verification code."""
    user = db.query(UserModel).filter(UserModel.verification_code == code).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    return user

def mark_user_as_verified(db: Session, user: UserModel) -> None:
    """Mark the user as verified and clear the verification code."""
    user.is_email_verified = True
    user.verification_code = None
    db.commit()
    db.refresh(user)
    
def create_unverified_user(db: Session, user_data: UserCreate):
    try:
        logging.info(f"Attempting to register user: {user_data.email}")
        
        existing_user = db.query(UserModel).filter(UserModel.email == user_data.email).first()
        logging.info(f"Existing user found: {existing_user is not None}")

        if existing_user and existing_user.is_email_verified:
            logging.info("User already verified.")
            raise HTTPException(status_code=400, detail="Email is already registered.")

        verification_code = generate_verification_code()
        logging.info(f"Generated verification code: {verification_code}")
        
        if existing_user:
            logging.info("Updating existing unverified user.")
            existing_user.full_name = user_data.full_name
            existing_user.hashed_password = get_password_hash(user_data.password)
            existing_user.verification_code = verification_code
            existing_user.verification_expiration = datetime.utcnow() + timedelta(hours=24)
            
            db.commit()
            db.refresh(existing_user)
            logging.info(f"Updated user with verification code: {existing_user.verification_code}")
        else:
            logging.info("Creating a new unverified user.")
            new_user = UserModel(
                email=user_data.email,
                full_name=user_data.full_name,
                hashed_password=get_password_hash(user_data.password),
                verification_code=verification_code,
                verification_expiration=datetime.utcnow() + timedelta(hours=24),
                is_email_verified=False
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            logging.info(f"New user created with ID: {new_user.id} and verification code: {new_user.verification_code}")
        
        return {"message": "User registered and verification email sent."}

    except Exception as e:
        logging.error(f"Error during user creation: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="User could not be created.")


def verify_user(db: Session, code: str):
    user = db.query(UserModel).filter(
        UserModel.verification_code == code,
        UserModel.verification_expiration >= datetime.utcnow()
    ).first()

    if not user or user.is_email_verified:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code.")

    user.is_email_verified = True
    db.commit()
    return {"message": "Email verified successfully."}

def verify_user_code(db: Session, code: str):
    print(f"Attempting to verify code: {code}")
    user = db.query(UserModel).filter(UserModel.verification_code == code).first()
    if not user:
        print("Verification code not found or invalid.")
    return user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)