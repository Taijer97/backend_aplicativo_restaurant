from pydantic import BaseModel
from typing import Optional

class MenuItemIn(BaseModel):
    name: str
    description: Optional[str]
    price: float
    category: Optional[str]
    amount: Optional[int] = 0
    available: Optional[bool] = True
    image_url: Optional[str] = None

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    amount: Optional[int] = None
    available: Optional[bool] = None
    image_url: Optional[str] = None

class MenuItemCreate(MenuItemIn):
    pass

class MenuItemOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    category: Optional[str]
    amount: Optional[int] = 0
    available: Optional[bool] = True
    image_url: Optional[str] = None

    class Config:
        orm_mode = True
