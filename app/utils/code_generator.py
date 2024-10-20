
import os

import random

SECRET_KEY = os.getenv("SECRET_KEY", "DbSLoIREJtu6z3CVnpTd_DdFeMMRoteCU0UjJcNreZI")  # Replace with your actual secret or use an environment variable



def generate_verification_code() -> str:
    """
    Generate a numeric verification code between 4 and 6 digits.
    """
    code_length = random.randint(4, 6)
    verification_code = ''.join([str(random.randint(0, 9)) for _ in range(code_length)])
    return verification_code