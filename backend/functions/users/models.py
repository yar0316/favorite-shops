from pydantic import BaseModel
from typing import Optional

class UserProfileResponse(BaseModel):
    user_id: str
    name: str
    picture: str
    email: str

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    picture: Optional[str] = None
