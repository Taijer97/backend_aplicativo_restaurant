# app/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base
import enum

# -------------------------------
# Enum roles
class UserRole(str, enum.Enum):
    admin = "admin"
    mozo = "mozo"
    cocina = "cocina"
    delivery = "delivery"
    cliente = "cliente"

# -------------------------------
# User
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    hashed_password = Column(String(200), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.cliente)

    orders = relationship("Order", back_populates="user")

# -------------------------------
# Table
class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False)
    seats = Column(Integer, default=4)
    location = Column(String(50), nullable=True)
    active = Column(Boolean, default=True)

    reservations = relationship("Reservation", back_populates="table")
    orders = relationship("Order", back_populates="table")

# -------------------------------
# MenuItem
class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    available = Column(Boolean, default=True)
    category = Column(String(50), nullable=True)

    order_items = relationship("OrderItem", back_populates="menu_item")

# -------------------------------
# Order
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=True)
    total = Column(Float, default=0)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="orders")
    table = relationship("Table", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

# -------------------------------
# OrderItem
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")

# -------------------------------
# Reservation
class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("tables.id"))
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    auto_cancel_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="active")

    table = relationship("Table", back_populates="reservations")