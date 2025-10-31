from sqlalchemy import Column, Integer, String, Float, Boolean
from db.base import Base
from sqlalchemy.orm import relationship

class SubCategory(Base):
    __tablename__ = "subcategories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    description = Column(String(255), nullable=True)
    img = Column(String(255), nullable=True)