from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    dni: str
    full_name: str
    email: str
    phone: str
    password: str
    role_id: int

class UserFull(BaseModel):
    id: int
    dni: str
    full_name: str
    email: str
    phone: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None

class UserOut(BaseModel):
    id: int
    role_id: int

    class Config:
        orm_mode = True
