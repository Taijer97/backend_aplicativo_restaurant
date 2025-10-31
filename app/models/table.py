from sqlalchemy import Column, Integer, String, Boolean
from db.base import Base
from sqlalchemy.orm import relationship

class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True)
    seats = Column(Integer)
    location = Column(String(100), nullable=True)
    active = Column(Boolean, default=True)

    orders = relationship("Order", back_populates="table")
    reservations = relationship("Reservation", back_populates="table")
