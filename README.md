# LiteHotel HMS (Admin CMS + Customer QR Ordering)

Production-lean, lightweight hotel/restaurant management system built with FastAPI + SQLite + Vanilla JS.

## Features
- Admin authentication (`/auth/login`) with Bearer token auth
- Admin CMS with modules: Dashboard, Tables, Orders, Menu, Inventory, Billing, Analytics, Settings
- Kitchen + Shop inventory with stock-in/stock-out and low-stock monitoring
- Order lifecycle and kitchen queue management
- Billing engine with settlement and receipts (`cash`, `upi`, `card`)
- Customer QR flow (`/menu/{table_token}`)
- CSV product import (`/products/upload`)
- Scalable API-first architecture with clean modules

## Tech stack
- **Backend:** FastAPI, SQLAlchemy
- **DB:** SQLite by default (switchable to PostgreSQL via `app/core/config.py`)
- **Frontend:** HTML, CSS, Vanilla JS (`fetch` + AJAX)

## Project structure
```
app/
  api/routes.py
  core/{config.py,database.py,security.py}
  models/{entities.py,__init__.py}
  schemas/{common.py,entities.py}
  services/{auth.py,billing.py}
  templates/{admin,index.html customer/index.html}
  static/{css,js}
  main.py
scripts/generate_qr.py
requirements.txt
```

## Database schema
Main tables:
- `users`
- `tables`
- `sessions`
- `orders`
- `order_items`
- `products`
- `inventory`
- `categories`
- `subcategories`
- `payments`

## Setup
1. Create venv and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run server:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Open:
   - Admin CMS: `http://localhost:8000/`
   - Customer view (example): `http://localhost:8000/menu/table-1-token`

## Default credentials
- Username: `admin`
- Password: `admin123`

## Core API endpoints
- `POST /auth/login`
- `GET /admin/stats`
- `GET|POST|PUT|DELETE /tables`
- `POST /sessions/start/{table_id}`
- `GET|POST|PUT|DELETE /products`
- `POST /products/upload`
- `GET|POST|PUT /inventory`
- `POST /inventory/purchase`
- `POST /orders`
- `GET /orders/kitchen`
- `PATCH /orders/{order_id}/status`
- `GET /billing/{table_session_id}`
- `GET /billing/session/{token}`
- `POST /billing/pay`
- `GET /analytics?period=today|tomorrow|weekly|monthly|yearly`

## Notes for production
- Move `secret_key` to environment variable.
- Use PostgreSQL and Alembic migrations.
- Add HTTPS, CORS policy, and reverse proxy.
- Add background workers/websockets for real-time kitchen screen updates.
- Harden RBAC roles (`admin`, `cashier`, `kitchen`, `manager`).
