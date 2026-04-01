from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import Category, DiningTable, InventoryItem, InventoryType, Product, User

app = FastAPI(title="LiteHotel HMS")
app.include_router(router)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).first():
            db.add(User(username="admin", full_name="System Admin", password_hash=hash_password("admin123")))
        if not db.query(DiningTable).first():
            db.add_all([DiningTable(name=f"T-{i}", qr_token=f"table-{i}-token") for i in range(1, 7)])
        if not db.query(Category).first():
            db.add_all([Category(name="Vegetables"), Category(name="Beverages"), Category(name="Main Course")])
        if not db.query(Product).first():
            db.add_all(
                [
                    Product(name="Paneer Curry", price=9.99, description="Rich curry", available=True),
                    Product(name="Lemon Soda", price=2.5, description="Fresh drink", available=True),
                    Product(name="Veg Biryani", price=7.25, description="Aromatic rice", available=True),
                ]
            )
        if not db.query(InventoryItem).first():
            db.add_all(
                [
                    InventoryItem(item_name="Paneer Curry", inventory_type=InventoryType.kitchen, category="Dairy", quantity=30),
                    InventoryItem(item_name="Lemon Soda", inventory_type=InventoryType.shop, category="Beverages", quantity=80),
                    InventoryItem(item_name="Veg Biryani", inventory_type=InventoryType.kitchen, category="Grains", quantity=40),
                ]
            )
        db.commit()
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def admin_page(request: Request):
    return templates.TemplateResponse("admin/index.html", {"request": request})


@app.get("/menu/{table_token}", response_class=HTMLResponse)
def customer_page(table_token: str, request: Request):
    return templates.TemplateResponse("customer/index.html", {"request": request, "table_token": table_token})
