import csv
import io
import secrets
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models import (
    Category,
    DiningTable,
    InventoryItem,
    Order,
    OrderItem,
    OrderStatus,
    Payment,
    Product,
    Session as TableSession,
    Subcategory,
    TableStatus,
    User,
)
from app.schemas.common import Message, TokenResponse
from app.schemas.entities import (
    CategoryCreate,
    InventoryCreate,
    InventoryPurchase,
    InventoryUpdate,
    LoginPayload,
    OrderCreate,
    OrderStatusUpdate,
    PaymentPayload,
    ProductCreate,
    ProductUpdate,
    SubcategoryCreate,
    TableCreate,
    TableUpdate,
)
from app.services.auth import get_current_user
from app.services.billing import compute_session_bill

router = APIRouter()


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(user.username))


@router.get("/admin/stats")
def admin_stats(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total_sales = db.query(func.coalesce(func.sum(Payment.amount), 0)).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()
    active_tables = db.query(func.count(TableSession.id)).filter(TableSession.is_active.is_(True)).scalar()
    low_stock = db.query(InventoryItem).filter(InventoryItem.quantity <= InventoryItem.low_stock_threshold).count()
    return {
        "total_sales": round(total_sales or 0, 2),
        "total_orders": total_orders,
        "active_tables": active_tables,
        "low_stock_alerts": low_stock,
    }


@router.get("/tables")
def list_tables(db: Session = Depends(get_db)):
    return db.query(DiningTable).all()


@router.post("/tables", response_model=Message)
def create_table(payload: TableCreate, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    table = DiningTable(name=payload.name, qr_token=secrets.token_urlsafe(12))
    db.add(table)
    db.commit()
    return Message(message="Table created")


@router.put("/tables/{table_id}", response_model=Message)
def update_table(table_id: int, payload: TableUpdate, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    table = db.query(DiningTable).filter(DiningTable.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    table.status = payload.status
    db.commit()
    return Message(message="Table updated")


@router.delete("/tables/{table_id}", response_model=Message)
def delete_table(table_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    table = db.query(DiningTable).filter(DiningTable.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    db.delete(table)
    db.commit()
    return Message(message="Table deleted")


@router.post("/sessions/start/{table_id}")
def start_session(table_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    table = db.query(DiningTable).filter(DiningTable.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    session = TableSession(table_id=table_id, token=secrets.token_urlsafe(10), is_active=True)
    table.status = TableStatus.busy
    db.add(session)
    db.commit()
    return {"session_id": session.id, "token": session.token}


@router.get("/products")
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@router.post("/products", response_model=Message)
def create_product(payload: ProductCreate, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.add(Product(**payload.model_dump()))
    db.commit()
    return Message(message="Product created")


@router.put("/products/{product_id}", response_model=Message)
def update_product(product_id: int, payload: ProductUpdate, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(product, key, value)
    db.commit()
    return Message(message="Product updated")


@router.delete("/products/{product_id}", response_model=Message)
def delete_product(product_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return Message(message="Product deleted")


@router.post("/products/upload", response_model=Message)
def upload_products(file: UploadFile = File(...), _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    for row in reader:
        db.add(Product(name=row["name"], price=float(row["price"]), available=row.get("available", "1") == "1"))
    db.commit()
    return Message(message="Products imported")


@router.get("/inventory")
def list_inventory(kind: str | None = None, db: Session = Depends(get_db)):
    query = db.query(InventoryItem)
    if kind:
        query = query.filter(InventoryItem.inventory_type == kind)
    return query.all()


@router.post("/inventory", response_model=Message)
def create_inventory(payload: InventoryCreate, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.add(InventoryItem(**payload.model_dump()))
    db.commit()
    return Message(message="Inventory item created")


@router.post("/inventory/purchase", response_model=Message)
def stock_in(payload: InventoryPurchase, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.id == payload.inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    item.quantity += payload.quantity
    db.commit()
    return Message(message="Stock updated")


@router.put("/inventory/{item_id}", response_model=Message)
def update_inventory(item_id: int, payload: InventoryUpdate, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(item, key, value)
    db.commit()
    return Message(message="Inventory updated")


@router.post("/orders")
def place_order(payload: OrderCreate, db: Session = Depends(get_db)):
    order = Order(session_id=payload.session_id, token=secrets.token_urlsafe(8), status=OrderStatus.pending)
    db.add(order)
    db.flush()
    for item in payload.items:
        product = db.query(Product).filter(Product.id == item.product_id, Product.available.is_(True)).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} unavailable")
        db.add(OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity, price=product.price))
        ingredient = db.query(InventoryItem).filter(InventoryItem.item_name == product.name).first()
        if ingredient:
            ingredient.quantity = max(0, ingredient.quantity - item.quantity)
    db.commit()
    return {"order_id": order.id, "token": order.token}


@router.get("/orders/kitchen")
def kitchen_view(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.status.in_([OrderStatus.pending, OrderStatus.preparing])).all()


@router.patch("/orders/{order_id}/status", response_model=Message)
def update_order_status(order_id: int, payload: OrderStatusUpdate, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = payload.status
    db.commit()
    return Message(message="Order status updated")


@router.get("/billing/{table_session_id}")
def get_bill(table_session_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return compute_session_bill(db, table_session_id)


@router.get("/billing/session/{token}")
def get_bill_by_token(token: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(TableSession.token == token).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return compute_session_bill(db, session.id)


@router.post("/billing/pay")
def make_payment(payload: PaymentPayload, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bill = compute_session_bill(db, payload.session_id)
    if bill["due"] <= 0:
        return {"message": "Already paid", "receipt": bill}
    payment = Payment(session_id=payload.session_id, amount=bill["due"], payment_method=payload.payment_method)
    db.add(payment)
    db.commit()
    bill = compute_session_bill(db, payload.session_id)
    return {"message": "Payment successful", "receipt": bill}


@router.get("/analytics")
def analytics(period: str = "today", _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    now = datetime.utcnow()
    start = datetime.combine(date.today(), datetime.min.time())
    if period == "tomorrow":
        start = start + timedelta(days=1)
    elif period == "weekly":
        start = now - timedelta(days=7)
    elif period == "monthly":
        start = now - timedelta(days=30)
    elif period == "yearly":
        start = now - timedelta(days=365)

    orders = db.query(Order).filter(Order.created_at >= start).count()
    revenue = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(Payment.paid_at >= start).scalar() or 0
    top_products = (
        db.query(Product.name, func.sum(OrderItem.quantity).label("qty"))
        .join(OrderItem, Product.id == OrderItem.product_id)
        .group_by(Product.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
        .all()
    )
    return {
        "period": period,
        "orders": orders,
        "sales": round(revenue, 2),
        "top_products": [{"name": name, "quantity": qty} for name, qty in top_products],
    }


@router.post("/categories", response_model=Message)
def create_category(payload: CategoryCreate, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.add(Category(name=payload.name))
    db.commit()
    return Message(message="Category created")


@router.post("/subcategories", response_model=Message)
def create_subcategory(payload: SubcategoryCreate, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.add(Subcategory(name=payload.name, category_id=payload.category_id))
    db.commit()
    return Message(message="Subcategory created")
