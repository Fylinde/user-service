import secrets
import random
import string
from app.models.user import UserModel

def create_session_token() -> str:
    return secrets.token_hex(16)


def verify_verification_code(user_obj, code):
    """
    Verify if the provided verification code matches the one stored in the user's record.
    """
    return user_obj.verification_code == code

def generate_otp(length=6):
    """Generate a random numeric OTP of a given length."""
    return ''.join(random.choices(string.digits, k=length))