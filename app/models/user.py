from pydantic.types import T
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.base import Base
import enum


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String(20), unique=True, index=True)
    full_name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, nullable=True)
    
    orders = relationship("models.order.Order", back_populates="user")