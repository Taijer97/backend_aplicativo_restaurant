from pydantic import BaseModel
from typing import Optional

class CategoryIn(BaseModel):
    id: Optional[int] = None
    name: str
    value: Optional[bool] = True
    img: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    value: Optional[bool] = None
    img: Optional[str] = None

class CategoryOut(BaseModel):
    id: int
    name: str
    value: bool
    img: Optional[str] = None

    class Config:
        orm_mode = True

