from pydantic import BaseModel
from typing import Optional

class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
    two_factor: Optional[bool] = None
    
class Token(BaseModel):
    access_token: str
    token_type: str    