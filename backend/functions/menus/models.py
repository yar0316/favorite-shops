from pydantic import BaseModel
from typing import List, Optional

class MenuBase(BaseModel):
    name: str
    photo_url: Optional[str] = None

class MenuCreate(MenuBase):
    pass

class MenuResponse(MenuBase):
    id: str
    shop_id: str
