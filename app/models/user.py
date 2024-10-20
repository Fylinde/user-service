# app/models/user.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import BaseModel
from app.models.association_tables import user_groups
from datetime import timedelta, datetime
from sqlalchemy import JSON
from sqlalchemy.orm import Session

import bcrypt

class UserModel(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    first_name = Column(String(128), nullable=True)
    middle_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String(20), nullable=True)
    hashed_password = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True)
    jwt_token_key = Column(String, nullable=True)  # <-- Add this column
    password_last_updated = Column(DateTime, nullable=True, default=datetime.utcnow)  # <-- New field
    # Preferences
    preferences = Column(JSON, nullable=True)  # Store user preferences as JSON
    notification_preferences = Column(String, nullable=True)  # Notification preferences
    verification_expiration = Column(DateTime, nullable=True)
    language_code = Column(String(35), default="en")
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    verification_code = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)  # Store as string for simplicity
    gender = Column(String(10), nullable=True)  # E.g., Male, Female, etc.
    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True)
    # New fields for seller dashboard and notifications
    notifications_enabled = Column(Boolean, default=True)  # Enable notifications for sellers
    ai_recommendation_opt_in = Column(Boolean, default=True)  # Sellers can opt in to AI recommendations
    
    # Relationships
   # addresses = relationship("AddressModel", back_populates="user")
    reviews = relationship("ReviewModel", back_populates="user")
   #orders = relationship("OrderModel", back_populates="user")
    wishlists = relationship("WishlistModel", back_populates="user")
    notes = relationship("CustomerNoteModel", back_populates="customer")
    events = relationship("CustomerEventModel", back_populates="customer")
    staff_notification = relationship("StaffNotificationRecipientModel", back_populates="user", uselist=False)
    groups = relationship("GroupModel", secondary=user_groups, back_populates="users")
    ai_recommendations = relationship("AIRecommendationModel", back_populates="user")  # New relationship to store AI recommendations
    notifications = relationship("NotificationModel", back_populates="user")
    
    
    created_at = Column(DateTime, default=datetime.utcnow)  # Automatically set account creation date
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Automatically update

    # Subscription and Roles
    subscription_status = Column(String, default="free")  # Subscription status, e.g., free, premium

    
    def get_full_name(self):
        """Return full name, which includes first, middle (if exists), and last name."""
        full_name = f"{self.first_name or ''} {self.middle_name or ''} {self.last_name or ''}".strip()
        return full_name or self.email

    def __repr__(self):
        return f'<User {self.full_name}>'
def create_unverified_user(db: Session, user_data):
    expiration_time = datetime.utcnow() + timedelta(hours=24)
    new_user = UserModel(
        email=user_data.email,
        full_name=user_data.full_name,
        verification_code=user_data.verification_code,
        verification_expiration=expiration_time,
        is_email_verified=False,
        # Other user fields...
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@staticmethod
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

                                