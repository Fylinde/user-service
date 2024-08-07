import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.models.user import UserModel
from app.database import get_db, SessionLocal
from passlib.context import CryptContext
from app.schemas.token import TokenData
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create a password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Create and include the router
router = APIRouter()

@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    logger.info("Received request to create user")
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        logger.error("Email already registered")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if db_user:
        logger.error("Username already registered")
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"Created user: {new_user}")

    return new_user

@router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Received request to read user with ID {user_id}")
    result = db.execute(select(UserModel).filter(UserModel.id == user_id))
    user = result.scalars().first()
    if user is None:
        logger.error("User not found")
        raise HTTPException(status_code=404, detail="User not found")
    return user

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

@router.put("/me", response_model=UserRead)
def update_user_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user is None:
        logger.error("Current user not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_data = user_update.dict(exclude_unset=True)

    for key, value in user_data.items():
        setattr(current_user, key, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user

@router.get("/{username}/profile", response_model=UserRead)
def read_public_profile(username: str, db: Session = Depends(get_db)):
    logger.info(f"Received request to read public profile for username {username}")
    result = db.execute(select(UserModel).filter(UserModel.username == username))
    user = result.scalars().first()
    if user is None:
        logger.error("User not found")
        raise HTTPException(status_code=404, detail="User not found")
    return user

logger.info("User routes defined successfully")


@router.get("/protected-endpoint", response_model=UserRead)
def protected_endpoint(current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    logging.info("Accessing protected endpoint")
    if current_user:
        logging.info(f"User ID: {current_user.id}, Username: {current_user.username}")
    else:
        logging.error("Current user is None")
    return current_user  # This will be converted to UserRead by FastAPI
