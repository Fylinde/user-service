from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    username: str
    email: EmailStr
    password: str
    profile_picture: Optional[str] = None
    preferences: Optional[str] = None

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True
        from_attributes = True  # Ensure this is set to True to enable from_orm functionality

class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    profile_picture: Optional[str]
    preferences: Optional[str]
