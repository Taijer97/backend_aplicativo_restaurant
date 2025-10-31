from sqlalchemy import Column, Integer, String, Float, Boolean
from db.base import Base
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    value = Column(Boolean, default=True)
    img = Column(String(255), nullable=True)
