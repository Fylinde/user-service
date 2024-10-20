import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import UserModel
from app.config import settings
import os
from app.schemas.token import TokenData
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Define constants
SECRET_KEY = os.getenv("SECRET_KEY", settings.SECRET_KEY)
ALGORITHM = os.getenv("ALGORITHM", settings.ALGORITHM)
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", settings.ACCESS_TOKEN_EXPIRE_MINUTES)

logger.info(f"SECRET_KEY: {SECRET_KEY}")
logger.info(f"ALGORITHM: {ALGORITHM}")

# Create an instance of OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create an instance of HTTPBearer for security
security = HTTPBearer()

# Create a context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to hash password
def get_password_hash(password):
    return pwd_context.hash(password)

# Function to create access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    to_encode.update({"sub": str(data["user_id"])})  # Ensure user_id is used as "sub"

    print(f"Token payload before encoding: {to_encode}")  # Log the token payload
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    print(f"Generated JWT: {encoded_jwt}")  # Log the generated JWT
    return encoded_jwt

# Function to authenticate user
def authenticate_user(db: Session, email: str, password: str) -> Optional[UserModel]:
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# Function to get current user
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.info(f"Token received: {token}")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.info(f"Decoded token payload: {payload}")

        user_id: int = payload.get("user_id")
        logger.info(f"Extracted user_id from token: {user_id}")

        if user_id is None:
            logger.error("User ID not found in token")
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError as e:
        logger.error(f"JWTError: {e}")
        raise credentials_exception

    user = db.query(UserModel).filter(UserModel.id == token_data.user_id).first()
    if user is None:
        logger.error(f"User not found: {token_data.user_id}")
        raise credentials_exception
    return user

# Function to get current user with admin check
def get_current_user_with_admin_check(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> UserModel:
    user = get_current_user(db=db, token=token)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return user

# Function to verify token
def verify_token(token: str) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin")
        if user_id is None:
            logging.error("Token payload does not contain 'sub'")
            raise credentials_exception
        token_data = TokenData(user_id=user_id, is_admin=is_admin)
        logging.info(f"Token validated successfully: {token_data}")
    except JWTError as e:
        logging.error(f"JWTError during token validation: {e}")
        raise credentials_exception
    return token_data

# Function to get current user from token
def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> TokenData:
    token = credentials.credentials
    try:
        payload = verify_token(token)
        logging.info(f"Payload from token: {payload}")
        return payload
    except JWTError as e:
        logging.error(f"JWTError: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Function to create password reset token
def create_password_reset_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to verify password reset token
def verify_password_reset_token(token: str) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logging.info(f"Payload from token: {payload}")
        user_id: str = payload.get("sub")
        if user_id is None:
            logging.error("User ID not found in token payload")
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError as e:
        logging.error(f"JWTError: {e}")
        raise credentials_exception
    return token_data

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)  # Typically, refresh tokens have a longer expiry
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_refresh_token(token: str) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.info(f"Token payload: {payload}")
        user_id = payload.get("user_id")
        if user_id is None:
            logger.error("No user_id in token payload")
            raise credentials_exception
        return TokenData(user_id=user_id)
    except JWTError as e:
        logger.error(f"JWTError during token validation: {e}")
        raise credentials_exception
    except Exception as e:
        logger.exception("Unexpected error during token validation")
        raise credentials_exception

# Function to verify if the user is an admin based on the token
def verify_admin_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if not payload.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Not authorized")
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
