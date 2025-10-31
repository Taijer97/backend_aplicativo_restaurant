from sqlalchemy import Column, Integer, String, Float, Boolean
from db.base import Base
from sqlalchemy.orm import relationship

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(255), nullable=True)
    price = Column(Float)
    category = Column(String(50), nullable=True)
    amount = Column(Integer, default=0)
    available = Column(Boolean, default=True)
    image_url = Column(String(255), nullable=True)

    order_items = relationship("OrderItem", back_populates="menu_item")
