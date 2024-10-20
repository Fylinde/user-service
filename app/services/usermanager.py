from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import UserModel
from app.schemas.user import UserUpdate
from app.models.notification import NotificationModel
from app.models.ai_recommendation import AIRecommendationModel
from uuid import uuid4
from datetime import datetime
from fastapi import HTTPException
from app.security import get_password_hash
import pyotp


class UserManager:

    @staticmethod
    def create_user(session: Session, email: str, phone_number: str, full_name: str, password: str, is_admin=False, **extra_fields):
        """Create a new regular user."""
        # Hash the password and create user entry
        hashed_password = get_password_hash(password)  # Make sure password is pre-processed if needed
        user = UserModel(
            email=email,
            phone_number=phone_number,
            full_name=full_name,
            hashed_password=hashed_password,
            jwt_token_key=str(uuid4().hex),  # Generate unique JWT key
            password_last_updated=datetime.utcnow(),
            is_admin=is_admin,
            **extra_fields
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


    @staticmethod
    def create_admin(session: Session, email: str, phone_number: str, full_name: str, password: str, **extra_fields):
        """Create a new admin user."""
        return UserManager.create_user(
            session=session, 
            email=email, 
            phone_number=phone_number,
            full_name=full_name,
            password=password, 
            is_admin=True, 
            **extra_fields
        )

    @staticmethod
    def check_password(user: UserModel, password: str) -> bool:
        """Check the provided password against the stored hashed password."""
        return check_password_hash(user.hashed_password, password)

    @staticmethod
    def update_password(session: Session, user: UserModel, new_password: str):
        """Update user's password."""
        user.hashed_password = generate_password_hash(new_password)
        user.password_last_updated = datetime.utcnow()
        session.commit()

    @staticmethod
    def get_user_by_id(session: Session, user_id: int):
        """Get a user by ID."""
        user = session.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def get_user_by_email(session: Session, email: str):
        """Get a user by email."""
        return session.query(UserModel).filter(UserModel.email == email).first()

    @staticmethod
    def update_user(session: Session, user: UserModel, user_update: UserUpdate):
        """Update user details."""
        user_data = user_update.dict(exclude_unset=True)
        for key, value in user_data.items():
            setattr(user, key, value)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    @staticmethod
    def delete_user(session: Session, user: UserModel):
        """Delete a user."""
        session.delete(user)
        session.commit()

    # --- Additional functionality for notifications ---
    
    @staticmethod
    def create_notification(session: Session, user_id: int, message: str):
        """Create a notification for a user."""
        notification = NotificationModel(
            user_id=user_id,
            message=message,
            is_read=False,
            date_created=datetime.utcnow()
        )
        session.add(notification)
        session.commit()
        session.refresh(notification)
        return notification

    @staticmethod
    def get_notifications_by_user(session: Session, user_id: int):
        """Get all notifications for a user."""
        return session.query(NotificationModel).filter(NotificationModel.user_id == user_id).all()

    # --- Additional functionality for AI Recommendations ---

    @staticmethod
    def create_ai_recommendation(session: Session, user_id: int, vendor_id: int, recommendation_data: dict, recommendation_type: str):
        """Create an AI recommendation for a user."""
        recommendation = AIRecommendationModel(
            user_id=user_id,
            vendor_id=vendor_id,
            recommendation_data=recommendation_data,
            recommendation_type=recommendation_type,
            date_created=datetime.utcnow()
        )
        session.add(recommendation)
        session.commit()
        session.refresh(recommendation)
        return recommendation

    @staticmethod
    def get_ai_recommendations_by_user(session: Session, user_id: int):
        """Get AI recommendations for a user."""
        return session.query(AIRecommendationModel).filter(AIRecommendationModel.user_id == user_id).all()
    
    # --- Additional utility functions (password reset, 2FA, etc.) ---
    
    @staticmethod
    def generate_reset_token(email: str):
        """Generate a password reset token for the user."""
        # You could generate a JWT token or some unique token here.
        return str(uuid4())
    
    @staticmethod
    def verify_reset_token(token: str):
        """Verify the password reset token."""
        # Logic to verify token (e.g., check expiration, etc.)
        pass

    @staticmethod
    def enable_2fa(session: Session, user: UserModel, secret: str):
        """Enable 2FA for the user."""
        user.two_factor_secret = secret
        user.two_factor_enabled = True
        session.commit()

    @staticmethod
    def verify_2fa_code(user: UserModel, code: str):
        """Verify 2FA code."""
        # Use pyotp to verify 2FA code.
        totp = pyotp.TOTP(user.two_factor_secret)
        return totp.verify(code)
    
    @staticmethod
    def disable_2fa(session: Session, user: UserModel):
        """Disable 2FA for the user."""
        user.two_factor_enabled = False
        user.two_factor_secret = None
        session.commit()
