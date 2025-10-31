from pydantic import BaseModel, Field
from typing import List, Optional
import datetime

class OrderItemIn(BaseModel):
    menu_item_id: int
    quantity: int = Field(gt=0)
    notes: Optional[str]

class CreateOrderIn(BaseModel):
    table_code: Optional[str]
    items: List[OrderItemIn]
    guest_name: Optional[str]
    guest_phone: Optional[str]
    delivery_address: Optional[str]

class OrderOut(BaseModel):
    id: int
    status: str
    total: float
    table_id: Optional[int]
    created_at: datetime.datetime

    class Config:
        orm_mode = True
