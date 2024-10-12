from pydantic import BaseModel, EmailStr, model_validator, field_validator, root_validator,FieldValidationInfo
from typing import Optional, List
from app.schemas.ai_recommendation import AIRecommendationResponse
from app.schemas.notification import NotificationResponse
from datetime import datetime

class UserBase(BaseModel):
    full_name: str  # Updated from username to full_name
    email: EmailStr
    phone_number: Optional[str]  # Added phone_number

    class Config:
        orm_mode = True
        
class UserCreate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: str
    password: str
    phone_number: Optional[str] = None
    profile_picture: Optional[str] = None
    preferences: Optional[str] = None
    verification_code: Optional[str] = None
    verification_expiration: Optional[datetime] = None
    is_email_verified: bool = False
    is_phone_verified: bool = False

    class Config:
        from_attributes = True

    @root_validator(pre=True)
    def check_email_or_phone(cls, values):
        email = values.get('email')
        phone_number = values.get('phone_number')
        
        if not email and not phone_number:
            raise ValueError('Either email or phone number must be provided')
        
        return values
    
class UserRead(BaseModel):
    id: int
    full_name: str  # Updated from username to full_name
    email: EmailStr
    phone_number: Optional[str] = None  # Added phone_number

    class Config:
        orm_mode = True
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str]  # Updated from username to full_name
    email: Optional[EmailStr]
    phone_number: Optional[str] = None  # Added phone_number
    password: Optional[str]
    profile_picture: Optional[str]
    preferences: Optional[str]
    is_admin: bool
    
class UserWithDetails(UserRead):
    notifications: List[NotificationResponse] = []  # Added notifications relationship
    ai_recommendations: List[AIRecommendationResponse] = []  # Added AI recommendations relationship

    class Config:
        orm_mode = True
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    full_name: str  # Change to full_name
    email: EmailStr
    phone_number: Optional[str] = None  # Add phone number in response
    is_active: bool
    is_admin: bool
    two_factor_enabled: bool
    failed_login_attempts: int
    account_locked: bool
    profile_picture: Optional[str] = None
    preferences: Optional[str] = None
    access_token: str
    
    class Config:
        orm_mode = True

# Schema for user info in a JWT token (minimal fields)
class TokenUser(BaseModel):
    id: int
    full_name: str  # Full name instead of username

    class Config:
        orm_mode = True

# Token response schema (used for login response)
class Token(BaseModel):
    access_token: str
    token_type: str        

class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: str

    @field_validator("phone_number", "email", mode="before")
    def validate_email_or_phone(cls, value, info: FieldValidationInfo):
        # Retrieve other fields from info.data
        email = info.data.get("email")
        phone_number = info.data.get("phone_number")
        
        if not email and not phone_number:
            raise ValueError("Either 'email' or 'phone_number' must be provided.")
        if email and phone_number:
            raise ValueError("Provide only one of 'email' or 'phone_number', not both.")
        
        return value
    
class OTPRequest(BaseModel):
    email: str = None
    phone_number: str = None
    carrier_gateway: str = None    

class UserSchema(BaseModel):
    id: int
    full_name: str  # Change to full_name
    email: str
    is_admin: bool

    class Config:
        orm_mode = True

class UserVerificationResponse(BaseModel):
    id: int
    full_name: str
    email: str
    is_email_verified: bool

    class Config:
        orm_mode = True

class UserAuthenticateRequest(BaseModel):
    username: str
    password: str

class UserAuthenticateResponse(BaseModel):
    id: str
    contact_info: str        