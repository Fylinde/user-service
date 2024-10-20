import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import (
    UserCreate, 
    UserRead, 
    UserUpdate 

)
from app.schemas.password import PasswordChangeRequest, PasswordResetRequest
from app.schemas.two_factor import Enable2FARequest, MessageResponse
from app.security import ( 
    get_current_user, 
    verify_password_reset_token
)
from app.utils.email_service import send_reset_email, generate_password_reset_token
from app.services.usermanager import UserManager
from app.database import get_db
from app.config import settings
from app.models.user import UserModel
from app.services.user_verification import verify_user_email_or_phone
from app.schemas.user import  UserLogin
from app.services.user_verification import verify_user_service, register_user_service
from app.schemas.user import UserAuthenticateRequest, UserAuthenticateResponse
from app.crud.user import verify_password
from app.utils.rabbitmq import RabbitMQConnection


router = APIRouter()

# Ensure this is an integer
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)

logger = logging.getLogger("user_routes")

# User Registration Route
@router.post("/register")
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return register_user_service(db, user_data)

@router.get("/verify")
async def verify_user(code: str, db: Session = Depends(get_db)):
    return verify_user_service(db, code)

# User Profile Retrieval (Current User)
@router.get("/me", response_model=UserRead)
def get_my_profile(current_user: UserModel = Depends(get_current_user)):
    """Retrieve the currently authenticated user's profile."""
    return current_user

# Update User Profile
@router.put("/me", response_model=UserRead)
def update_user_profile(
    user_update: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """Update the currently authenticated user's profile."""
    updated_user = UserManager.update_user(db, current_user, user_update)
    return updated_user

# Password Reset Request
@router.post("/password-reset-request", response_model=MessageResponse)
def password_reset_request(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Send a password reset token to the user's email."""
    user = UserManager.get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = generate_password_reset_token(request.email)
    send_reset_email(request.email, reset_token)
    return {"message": "Password reset token sent"}

# Password Reset
@router.post("/password-reset", response_model=MessageResponse)
def password_reset(reset: PasswordChangeRequest, db: Session = Depends(get_db)):
    """Reset the user's password using a token."""
    email = verify_password_reset_token(reset.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = UserManager.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    UserManager.update_password(db, user, reset.new_password)
    return {"message": "Password has been reset successfully"}

# Enable 2FA
@router.post("/enable-2fa", response_model=MessageResponse)
def enable_2fa(request: Enable2FARequest, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """Enable 2FA for the current user."""
    UserManager.enable_2fa(db, current_user, request.secret)
    return {"message": "2FA enabled successfully"}

# Disable 2FA
@router.post("/disable-2fa", response_model=MessageResponse)
def disable_2fa(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """Disable 2FA for the current user."""
    UserManager.disable_2fa(db, current_user)
    return {"message": "2FA disabled successfully"}

# Delete User
@router.delete("/me", response_model=MessageResponse)
def delete_user_profile(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """Delete the currently authenticated user's profile."""
    UserManager.delete_user(db, current_user)
    return {"message": "User deleted successfully"}

# Logout (Invalidate Token)
@router.post("/logout", response_model=MessageResponse)
def logout_user():
    """Invalidate the user's session/token."""
    # Logic for logging out (e.g., invalidating token, clearing session)
    return {"message": "User logged out successfully"}


@router.get("/verify-code")
async def verify_code_endpoint(code: str, db: Session = Depends(get_db)):
    logging.info(f"Received verification request with code: {code}")

    # Query the user by verification code
    user = db.query(UserModel).filter(UserModel.verification_code == code).first()

    if not user:
        logging.info("Verification code is invalid or not found.")
        raise HTTPException(status_code=404, detail="Verification code is invalid.")
    
    # Mark the user as verified and save
    user.is_email_verified = True
    db.commit()
    logging.info(f"User {user.id} marked as verified.")

    # Prepare user data for publishing
    user_data = {
        "id": user.id,
        "email": user.email,
        "phone": user.phone_number,
        "full_name": user.full_name,
        "is_verified": user.is_email_verified,
    }

    # Publish user data to RabbitMQ
    try:
        # Specify queue_name during connection creation if missing
        rabbitmq = RabbitMQConnection(queue_name='user_verification_queue')
        
        # Alternatively, provide routing_key directly to publish_message method
        rabbitmq.publish_message(user_data, routing_key='user_verification_queue')
        logging.info(f"Published user {user.id} verification to RabbitMQ.")
    except Exception as e:
        logging.error(f"Failed to publish user {user.id} to RabbitMQ: {e}")
    finally:
        rabbitmq.close_connection()

    return {
        "verified": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "verified": user.is_email_verified
        }
    }
    
@router.post("/verify")
def verify_user_endpoint(code: str, db: Session = Depends(get_db)):
    return verify_user_email_or_phone(code, db)


@router.post("/login")
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(
        (UserModel.email == user_login.email_or_phone) | 
        (UserModel.phone_number == user_login.email_or_phone)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if not UserManager.check_password(user, user_login.password):
        raise HTTPException(status_code=403, detail="Invalid credentials.")
    if not user.is_email_verified:
        raise HTTPException(status_code=403, detail="Email not verified.")

    # Return a complete user object
    return {
        "id": user.id,
        "email": user.email,
        "phone_number": user.phone_number,
        "full_name": user.full_name,
        "verified": user.is_email_verified
    }


@router.post("/authenticate", response_model=UserAuthenticateResponse)
def authenticate_user(
    data: UserAuthenticateRequest,
    db: Session = Depends(get_db)
):
    user = db.query(UserModel).filter(
        (UserModel.email == data.username) | (UserModel.phone_number == data.username)
    ).first()
    
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Convert id to string for the response model
    return {
        "id": str(user.id),  # Ensure the ID is returned as a string
        "contact_info": user.email if user.email else user.phone_number,
    }

@router.get("/get-by-contact")
def get_user_by_contact(contact: str, db: Session = Depends(get_db)):
    # Find the user by email or phone number
    user = db.query(UserModel).filter(
        (UserModel.email == contact) | (UserModel.phone_number == contact)
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return necessary user information for the auth-service
    return {
        "id": str(user.id),
        "contact_info": user.email if user.email else user.phone_number,
        "two_factor_enabled": user.two_factor_enabled
    }