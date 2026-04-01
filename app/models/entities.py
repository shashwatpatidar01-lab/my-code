from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TableStatus(str, Enum):
    available = "available"
    reserved = "reserved"
    busy = "busy"


class OrderStatus(str, Enum):
    pending = "pending"
    preparing = "preparing"
    served = "served"
    cancelled = "cancelled"


class PaymentMethod(str, Enum):
    cash = "cash"
    upi = "upi"
    card = "card"


class InventoryType(str, Enum):
    kitchen = "kitchen"
    shop = "shop"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    subcategories: Mapped[list["Subcategory"]] = relationship(back_populates="category")


class Subcategory(Base):
    __tablename__ = "subcategories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped[Category] = relationship(back_populates="subcategories")


class DiningTable(Base):
    __tablename__ = "tables"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    status: Mapped[TableStatus] = mapped_column(SAEnum(TableStatus), default=TableStatus.available)
    qr_token: Mapped[str] = mapped_column(String(120), unique=True, index=True)


class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("tables.id"), index=True)
    token: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    price: Mapped[float] = mapped_column(Float)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    available: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str] = mapped_column(Text, default="")


class InventoryItem(Base):
    __tablename__ = "inventory"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_name: Mapped[str] = mapped_column(String(120), index=True)
    inventory_type: Mapped[InventoryType] = mapped_column(SAEnum(InventoryType), index=True)
    category: Mapped[str] = mapped_column(String(80))
    subcategory: Mapped[str] = mapped_column(String(80), default="general")
    unit: Mapped[str] = mapped_column(String(20), default="pcs")
    quantity: Mapped[float] = mapped_column(Float, default=0)
    low_stock_threshold: Mapped[float] = mapped_column(Float, default=10)


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.pending)
    token: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)


class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    amount: Mapped[float] = mapped_column(Float)
    payment_method: Mapped[PaymentMethod] = mapped_column(SAEnum(PaymentMethod))
    paid_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
