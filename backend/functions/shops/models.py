from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ShopBase(BaseModel):
    name: str
    area: str
    address: Optional[str] = None
    cuisine_genres: List[str]
    drink_genres: List[str]
    comment: Optional[str] = None
    photos: List[str] = []
    external_link: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ShopCreate(ShopBase):
    pass

class ShopResponse(ShopBase):
    id: str
    created_by: str
    group_id: str
    created_at: datetime
    updated_at: datetime

class ShopListResponse(BaseModel):
    shops: List[ShopResponse]
    total: int

class ShopParseRequest(BaseModel):
    url: str

class ParsedShopResponse(ShopBase):
    pass
