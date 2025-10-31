from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from db.base import Base

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("tables.id"))
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    status = Column(String(50), default="pending")

    table = relationship("Table", back_populates="reservations")
