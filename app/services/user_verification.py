import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import UserModel
from app.crud.user import verify_user
from app.utils.email_service import send_verification_email
from app.utils.code_generator import generate_verification_code
from datetime import datetime, timedelta
from app.schemas.user import UserCreate
from app.utils.password_validation import get_password_hash

logger = logging.getLogger(__name__)

def verify_user_email_or_phone(code: str, db: Session):
    """
    Verify user by updating the is_verified status for either email or phone.
    """
    user = db.query(UserModel).filter(
        (UserModel.verification_code == code) & 
        (UserModel.is_verified.is_(False))
    ).first()

    if not user:
        logger.warning(f"No user found with verification code {code}.")
        raise HTTPException(status_code=400, detail="Invalid or expired verification code.")

    # Check if the code is for email or phone verification
    if user.email_verification_code == code:
        user.is_email_verified = True
        user.email_verification_code = None
    elif user.phone_verification_code == code:
        user.is_phone_verified = True
        user.phone_verification_code = None

    # Set user as verified if either email or phone verification is completed
    if user.is_email_verified or user.is_phone_verified:
        user.is_verified = True

    # Commit changes to mark the user as verified
    db.commit()
    logger.info(f"User {user.email or user.phone} verified.")

    return {"message": f"User {user.email or user.phone} has been verified."}



def register_user_service(db: Session, user_data: UserCreate):
    existing_user = db.query(UserModel).filter(UserModel.email == user_data.email).first()

    if existing_user and existing_user.is_email_verified:
        raise HTTPException(status_code=400, detail="Email is already registered.")

    # Generate verification code
    verification_code = generate_verification_code()
    logging.info(f"Generated verification code: {verification_code}")

    if existing_user:
        existing_user.verification_code = verification_code
        existing_user.verification_expiration = datetime.utcnow() + timedelta(hours=24)
    else:
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
    logging.info("Verification code saved to the database.")

    # Send verification email after saving the code to ensure synchronization
    send_verification_email(user_data.email, verification_code)


def verify_user_service(db: Session, code: str):
    return verify_user(db, code)