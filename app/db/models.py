from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, DECIMAL
from sqlalchemy.orm import relationship
from .database import Base
import enum
import datetime

class RoleEnum(str, enum.Enum):
    admin = "admin"
    mozo = "mozo"
    cocina = "cocina"
    caja = "caja"
    delivery = "delivery"
    cliente = "cliente"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    hashed_password = Column(String(255), nullable=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.cliente)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), unique=True, index=True)
    seats = Column(Integer, default=4)
    location = Column(String(255), nullable=True)
    active = Column(Boolean, default=True)

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10,2), nullable=False)
    category = Column(String(100), nullable=True)
    available = Column(Boolean, default=True)
    image_url = Column(String(500), nullable=True)

class OrderStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    ready = "ready"
    delivered = "delivered"
    paid = "paid"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    total = Column(DECIMAL(10,2), default=0)
    delivery_address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User")
    table = relationship("Table")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer, default=1)
    price = Column(DECIMAL(10,2), default=0)
    notes = Column(Text, nullable=True)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    table_id = Column(Integer, ForeignKey("tables.id"))
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    status = Column(String(32), default="pending")
    auto_cancel_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User")
    table = relationship("Table")