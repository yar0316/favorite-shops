from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class GroupCreate(BaseModel):
    name: str

class GroupResponse(BaseModel):
    id: str
    name: str
    owner_id: str
    created_at: datetime

class GroupMemberResponse(BaseModel):
    user_id: str
    name: str
    role: str

class InvitationResponse(BaseModel):
    code: str
    group_id: str
    expires_at: datetime

class JoinRequest(BaseModel):
    code: str
