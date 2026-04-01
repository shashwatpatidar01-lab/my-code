from pydantic import BaseModel

from app.models import InventoryType, OrderStatus, PaymentMethod, TableStatus


class LoginPayload(BaseModel):
    username: str
    password: str


class TableCreate(BaseModel):
    name: str


class TableUpdate(BaseModel):
    status: TableStatus


class SessionStart(BaseModel):
    table_id: int


class ProductCreate(BaseModel):
    name: str
    price: float
    category_id: int | None = None
    available: bool = True
    description: str = ""


class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    category_id: int | None = None
    available: bool | None = None
    description: str | None = None


class InventoryCreate(BaseModel):
    item_name: str
    inventory_type: InventoryType
    category: str
    subcategory: str = "general"
    unit: str = "pcs"
    quantity: float = 0
    low_stock_threshold: float = 10


class InventoryPurchase(BaseModel):
    inventory_id: int
    quantity: float


class InventoryUpdate(BaseModel):
    item_name: str | None = None
    category: str | None = None
    subcategory: str | None = None
    unit: str | None = None
    quantity: float | None = None
    low_stock_threshold: float | None = None


class OrderItemPayload(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    session_id: int
    items: list[OrderItemPayload]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class PaymentPayload(BaseModel):
    session_id: int
    payment_method: PaymentMethod


class CategoryCreate(BaseModel):
    name: str


class SubcategoryCreate(BaseModel):
    name: str
    category_id: int
