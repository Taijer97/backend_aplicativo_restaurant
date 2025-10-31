from pydantic import BaseModel
import datetime

class ReservationIn(BaseModel):
    table_id: int
    start_at: datetime.datetime
    end_at: datetime.datetime

class ReservationOut(BaseModel):
    id: int
    table_id: int
    start_at: datetime.datetime
    end_at: datetime.datetime
    status: str

    class Config:
        orm_mode = True
