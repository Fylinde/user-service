from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional, List
from app.schemas.ai_recommendation import AIRecommendationResponse
from app.schemas.notification import NotificationResponse

class VendorBase(BaseModel):
    id: Optional[int]
    full_name: str  # Updated from username to full_name
    email: EmailStr
    phone_number: Optional[str]  # Added phone_number

    class Config:
        orm_mode = True
        
class VendorCreate(VendorBase):
    email: EmailStr
    full_name: str  # Full name for creation
    password: str
    phone_number: Optional[str] = None  # Add phone number for user registration
    profile_picture: Optional[str] = None
    preferences: Optional[str] = None

    class Config:
        orm_mode = True

    # Use @model_validator for cross-field validation in Pydantic V2
    @model_validator(mode='before')
    @classmethod
    def check_email_or_phone(cls, values):
        email = values.get('email')
        phone_number = values.get('phone_number')
        
        if not email and not phone_number:
            raise ValueError('Either email or phone number must be provided')
        
        return values

class VendorRead(BaseModel):
    id: int
    full_name: str  # Updated from username to full_name
    email: EmailStr
    phone_number: Optional[str] = None  # Added phone_number

    class Config:
        orm_mode = True
        from_attributes = True

class VendorUpdate(BaseModel):
    full_name: Optional[str]  # Updated from username to full_name
    email: Optional[EmailStr]
    phone_number: Optional[str] = None  # Added phone_number
    password: Optional[str]
    profile_picture: Optional[str]
    preferences: Optional[str]
    is_admin: bool
    
class VendorWithDetails(VendorRead):
    notifications: List[NotificationResponse] = []  # Added notifications relationship
    ai_recommendations: List[AIRecommendationResponse] = []  # Added AI recommendations relationship

    class Config:
        orm_mode = True
        from_attributes = True

class VendorResponse(BaseModel):
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
    
#class UserWithOrders(UserResponse):
 #   orders: List["OrderResponse"] = []  # If OrderResponse isn't defined, consider importing or removing it

class VendorLogin(BaseModel):
    email_or_phone: str  # Allow login with either email or phone number
    password: str
    
class OTPRequest(BaseModel):
    email: str = None
    phone_number: str = None
    carrier_gateway: str = None    

class VendorSchema(BaseModel):
    id: int
    full_name: str  # Change to full_name
    email: str
    is_admin: bool

    class Config:
        orm_mode = True
