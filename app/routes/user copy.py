from fastapi import Form, APIRouter, Depends, HTTPException, status, Security, Request, BackgroundTasks
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.crud.session_crud import create_session  # Import session creation logic
from app.security import (
    oauth2_scheme,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user,

    verify_refresh_token,
    authenticate_user,
    TokenData
)
from app.dependencies import get_db
from app.models.user import UserModel
from app.models.session import Session as SessionModel
from app.schemas.user_schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    UserUpdate, 
    OTPRequest 
)
from app.schemas.two_factor import Enable2FARequest, TwoFactorEnableRequest, Message
from app.schemas.password import PasswordChangeRequest, PasswordReset, PasswordResetRequest
from app.schemas.session_schemas import SessionCreate, SessionResponse
from app.schemas.token import Token, TokenRefresh, TokenResponse
from app.utils.token_utils import verify_verification_code, generate_verification_code, generate_otp
# from app.utils.email import 
from app.utils.password_utils import get_password_hash, validate_password
import pyotp
import uuid
import os
import pika
import json
import random
import string
import requests
import logging
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from typing import Optional, List
from app.config import settings
from app.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token
)

from app.database import SessionLocal, get_db
from app.utils.rabbitmq import publish_user_created_event
from fastapi.responses import RedirectResponse
from app.utils.email_service import send_otp_via_email, send_sms_via_email, send_reset_email, generate_password_reset_token, verify_password_reset_token, send_verification_email, generate_verification_token
from app.services.usermanager import UserManager



router = APIRouter()

def get_background_tasks():
    return BackgroundTasks()

# Ensure this is an integer
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#logger = logging.getLogger(__name__)

# Define a time window (e.g., 5 minutes) for OTP expiration
OTP_VALIDITY_DURATION = timedelta(minutes=5)

# Set up logging
logger = logging.getLogger("auth_service")

logging.basicConfig(level=logging.INFO)
@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting to register user with full name: {user.full_name} and email: {user.email}")

    try:
        # Check if the user already exists (by email or phone number)
        existing_user = db.query(UserModel).filter(
            (UserModel.email == user.email) | (UserModel.phone_number == user.phone_number)
        ).first()

        if existing_user:
            logger.warning(f"Registration failed: User with email '{user.email}' already exists")
            raise HTTPException(status_code=400, detail="Email already registered")

        # Use UserManager to create the user (UserManager handles password hashing)
        new_user = UserManager.create_user(
            session=db, 
            email=user.email, 
            phone_number=user.phone_number,
            full_name=user.full_name,
            password=user.password  # UserManager will handle hashing
        )

        logger.info(f"New user created with ID: {new_user.id}, full name: {new_user.full_name}, email: {new_user.email}")

        # Generate a verification code and save it to the new user
        verification_code = generate_verification_code()
        new_user.verification_code = verification_code  # Store the verification code in the UserModel
        logger.info(f"Generated verification code for user {new_user.full_name}: {verification_code}")

        db.commit()  # Commit the new user and the verification code to the database
        db.refresh(new_user)

        # Correctly passing user_id in the data payload
        access_token = create_access_token(data={"user_id": new_user.id})

        # Prepare user data for RabbitMQ publishing
        user_data = {
            "id": new_user.id,
            "full_name": new_user.full_name,
            "email": new_user.email,
            "hashed_password": new_user.hashed_password,
            "profile_picture": user.profile_picture,
            "preferences": user.preferences,
            "two_factor_enabled": new_user.two_factor_enabled,
            "two_factor_secret": new_user.two_factor_secret,
        }

        # Publish event to RabbitMQ
        publish_user_created_event(user_data)
        logger.info(f"Publishing user creation event for {new_user.full_name} (ID: {new_user.id}) to RabbitMQ")

        # Send the verification email
        send_verification_email(new_user.email, verification_code)
        logger.info(f"Sent verification email to {new_user.email}")

        return {
            "id": new_user.id,
            "full_name": new_user.full_name,
            "email": new_user.email,
            "phone_number": new_user.phone_number,
            "is_active": new_user.is_active,
            "is_admin": new_user.is_admin,
            "two_factor_enabled": new_user.two_factor_enabled,
            "failed_login_attempts": new_user.failed_login_attempts,
            "account_locked": new_user.account_locked,
            "profile_picture": user.profile_picture,
            "preferences": user.preferences,
            "access_token": access_token,  # Return token
            "token_type": "bearer"
        }

    except Exception as e:
        logger.error(f"Error during user registration: {e}")
        db.rollback()  # Rollback the transaction if any error occurs
        raise HTTPException(status_code=500, detail="An error occurred during registration")


        
@router.get("/verify")
async def verify_email(code: str, db: Session = Depends(get_db)):
    logger.info(f"Verifying user with verification code: {code}")

    # Fetch the user by the verification code
    user = db.query(UserModel).filter(UserModel.verification_code == code).first()

    if not user:
        logger.error(f"Invalid or expired verification code: {code}")
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")

    # Mark user as verified and clear the verification code
    user.is_verified = True
    user.verification_code = None  # Clear the token after successful verification
    db.commit()

    logger.info(f"User {user.full_name} successfully verified")

    # Automatically sign the user in by generating an access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id, "is_admin": user.is_admin},  # Replaced role with is_admin
        expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=7)
    refresh_token = create_refresh_token(
        data={"user_id": user.id}, expires_delta=refresh_token_expires
    )

    logger.info(f"Access token and refresh token generated for user {user.full_name}")

    # Construct the redirect URL with the access_token and refresh_token
    redirect_url = f"http://localhost:3000/user-dashboard?access_token={access_token}&refresh_token={refresh_token}"

    # Redirect to the user dashboard in the frontend
    return RedirectResponse(url=redirect_url)

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    login_identifier = form_data.username  # Use the username or email field
    password = form_data.password

    # Fetch the user by email or phone number
    user = db.query(UserModel).filter(
        (UserModel.email == login_identifier) | (UserModel.phone_number == login_identifier)
    ).first()

    if not user or not UserManager.check_password(user, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create access and refresh tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id, "is_admin": user.is_admin},
        expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=7)
    refresh_token = create_refresh_token(
        data={"user_id": user.id}, expires_delta=refresh_token_expires
    )

    # Create a session token and save it in the session table
    session_token_expires = datetime.utcnow() + timedelta(hours=1)  # Session expires in 1 hour
    session_token = create_access_token(  # Generate a session token using the same method as access_token
        data={"user_id": user.id},
        expires_delta=timedelta(hours=1)  # Session token expiry
    )

    # Save the session in the database
    create_session(db=db, session=SessionCreate(
        user_id=user.id,
        session_token=session_token,
        expires_at=session_token_expires,
        is_valid=True
    ))

    # Return tokens including the session token
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "session_token": session_token,  # Add session token to the response
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "is_admin": user.is_admin,
        }
    }


@router.post("/password-reset-request", response_model=Message)
def password_reset_request(request: PasswordResetRequest, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == request.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = generate_password_reset_token(request.email)
    send_reset_email(request.email, reset_token)
    return {"message": "Password reset token sent"}

@router.post("/password-reset")
def password_reset(reset: PasswordReset, db: Session = Depends(get_db)):
    email = verify_password_reset_token(reset.token)
    if email is None:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    db_user = db.query(UserModel).filter(UserModel.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not validate_password(reset.new_password):
        raise HTTPException(status_code=400, detail="Password does not meet the strength requirements")

    db_user.hashed_password = get_password_hash(reset.new_password)
    db_user.password_last_updated = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return {"message": "Password has been reset successfully"}

@router.post("/token-refresh", response_model=Token)
def refresh_token(token_refresh: TokenRefresh, db: Session = Depends(get_db)):
    logger.info(f"Received refresh token: {token_refresh.refresh_token}")
    token_data = verify_refresh_token(token_refresh.refresh_token)
    logger.info(f"Verified token data: user_id={token_data.user_id} full_name={token_data.full_name} role={token_data.role} two_factor={token_data.two_factor}")

    db_user = db.query(UserModel).filter(UserModel.id == token_data.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.full_name, "user_id": db_user.id, "role": db_user.role},
        expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=7)
    refresh_token = create_refresh_token(
        data={"user_id": db_user.id}, expires_delta=refresh_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

def generate_backup_codes() -> list:
    return [''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) for _ in range(10)]


@router.post("/enable-2fa", response_model=Message)
def enable_2fa(data: Enable2FARequest, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("user_id")
    
    if user_id is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    totp = pyotp.TOTP(db_user.two_factor_secret)
    expected_code = totp.now()

    if not totp.verify(data.code, valid_window=1):
        raise HTTPException(status_code=400, detail="Invalid 2FA code")

    db_user.two_factor_enabled = True
    db.commit()

    return {"message": "2FA enabled successfully"}



@router.post("/disable-2fa", response_model=Message)
def disable_2fa(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("user_id")

    if user_id is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.two_factor_enabled = False
    db.commit()

    return {"message": "2FA disabled successfully"}

@router.post("/verify-2fa", response_model=Token)
def verify_2fa(data: Enable2FARequest, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("user_id")

    if user_id is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    totp = pyotp.TOTP(db_user.two_factor_secret)
    if not totp.verify(data.code, valid_window=1):
        raise HTTPException(status_code=400, detail="Invalid 2FA code")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": db_user.id, "role": db_user.role}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=7)
    refresh_token = create_access_token(
        data={"user_id": db_user.id}, expires_delta=refresh_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@router.get("/test-2fa", response_model=Message)
def test_2fa(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("user_id")

    if user_id is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not db_user.two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA is not enabled")

    return {"message": "2FA is enabled and working correctly"}

@router.get("/generate-2fa-code", response_model=Enable2FARequest)
def generate_2fa_code(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("user_id")

    if user_id is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    totp = pyotp.TOTP(db_user.two_factor_secret)
    current_code = totp.now()

    return {"code": current_code}


@router.post("/login")
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.full_name, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect full_name or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id, "full_name": user.full_name, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/sessions", response_model=List[SessionResponse])
def list_sessions(db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    sessions = db.query(Session).filter(Session.user_id == current_user.id).all()
    return sessions

@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    session = db.query(Session).filter(Session.id == session_id, Session.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"message": "Session deleted successfully"}

@router.get("/verify-user/{full_name}", response_model=UserResponse)
def verify_user(full_name: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.full_name == full_name).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/profile", response_model=UserResponse)
def update_profile(user_update: UserUpdate, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    db_user = db.query(UserModel).filter(UserModel.full_name == current_user.full_name).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.full_name:
        db_user.full_name = user_update.full_name
    if user_update.email:
        if db.query(UserModel).filter(UserModel.email == user_update.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        db_user.email = user_update.email
    if user_update.password:
        db_user.hashed_password = pwd_context.hash(user_update.password)
    if user_update.role:
        db_user.role = user_update.role
    
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_id_from_token(token: str, db: Session):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    logger.info(f"Extracted user_id from token: {user_id}")
    return user_id

@router.post("/send-otp")
async def send_otp(
    email: str = Form(None),
    phone_number: str = Form(None),
    carrier_gateway: str = Form(None),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    if not email and not phone_number:
        raise HTTPException(status_code=400, detail="Email or phone number must be provided")

    otp = generate_otp()
    otp_generated_at = datetime.utcnow()
    logger.info(f"Generated OTP: {otp}")  # Log the generated OTP
    user_id = get_user_id_from_token(token, db)

    if email:
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        send_otp_via_email(email, otp)

    if phone_number and carrier_gateway:
        send_sms_via_email(phone_number, otp, carrier_gateway)

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    user.otp_code = otp
    user.otp_generated_at = otp_generated_at
    logger.info(f"Saving OTP for user_id {user_id} in the database: {otp}")  # Log OTP being saved
    db.commit()

    return {"message": "OTP sent successfully"}

@router.post("/verify-otp")
def verify_otp(contact: str, otp: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == contact).first() if "@" in contact else db.query(UserModel).filter(UserModel.phone == contact).first()
    
    if not user:
        logger.error(f"User not found for contact: {contact}")  # Log if user is not found
        raise HTTPException(status_code=404, detail="User not found")
        # Check if the OTP is within the valid time window
        
    if datetime.utcnow() - user.otp_generated_at > OTP_VALIDITY_DURATION:
        raise HTTPException(status_code=400, detail="OTP has expired")

    logger.info(f"Verifying OTP for user: {user.id}. Provided OTP: {otp}, Stored OTP: {user.otp_code}")
    
    if user.otp_code != otp:
        logger.error(f"Invalid OTP for user_id {user.id}. Provided: {otp}, Expected: {user.otp_code}")
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user.otp_code = None  # Clear the OTP after verification
    db.commit()

    logger.info(f"OTP verification successful for user_id {user.id}")
    return {"message": "OTP verified successfully"}
