from pydantic import BaseModel
from typing import Optional

class TableOut(BaseModel):
    id: int
    code: str
    seats: int
    location: Optional[str]
    active: bool

    class Config:
        orm_mode = True
