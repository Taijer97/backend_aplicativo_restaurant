from pydantic import BaseModel
from typing import Optional

# ✅ Esquema para crear subcategorías
class SubCategoryIn(BaseModel):
    name: str
    description: Optional[str] = None
    img: Optional[str] = None


# ✅ Esquema para actualizar (campos opcionales)
class SubCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    img: Optional[str] = None


# ✅ Esquema para devolver datos (con ID)
class SubCategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    img: Optional[str] = None

    class Config:
        orm_mode = True