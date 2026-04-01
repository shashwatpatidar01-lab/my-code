from sqlalchemy.orm import Session

from app.models import Order, OrderItem, Payment, Session as TableSession


def compute_session_bill(db: Session, session_id: int) -> dict:
    session_obj = db.query(TableSession).filter(TableSession.id == session_id).first()
    if not session_obj:
        return {"session_id": session_id, "items": [], "total": 0}

    orders = db.query(Order).filter(Order.session_id == session_id).all()
    item_rows = []
    total = 0.0
    for order in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in items:
            subtotal = item.price * item.quantity
            total += subtotal
            item_rows.append(
                {
                    "order_id": order.id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": item.price,
                    "subtotal": subtotal,
                }
            )

    paid = sum(p.amount for p in db.query(Payment).filter(Payment.session_id == session_id).all())
    return {
        "session_id": session_id,
        "token": session_obj.token,
        "items": item_rows,
        "total": round(total, 2),
        "paid": round(paid, 2),
        "due": round(total - paid, 2),
    }
