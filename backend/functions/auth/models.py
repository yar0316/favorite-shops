from pydantic import BaseModel

class AuthRequest(BaseModel):
    idToken: str

class AuthResponse(BaseModel):
    user_id: str
    name: str
    picture: str
    is_new_user: bool
