import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from backend.deps import get_db, require_csrf, require_session
from backend.models.order import NewOrderRequest, UpdateOrderStatusRequest
from backend.models.payment import NewPaymentRequest
from backend.validators import (
    VALID_PAYMENT_METHODS,
    VALID_PAYMENT_TYPES,
    VALID_STATUSES,
    clean_text,
    is_valid_date,
    is_valid_price,
)

router = APIRouter(prefix="/api", tags=["orders"])


@router.get("/orders")
def list_orders(status: str | None = None, session: dict = Depends(require_session), db: sqlite3.Connection = Depends(get_db)):
    base_query = """SELECT o.*, c.name AS customer_name, c.phone AS customer_phone
                     FROM orders o JOIN customers c ON c.customer_id = o.customer_id"""
    if status and status in VALID_STATUSES:
        rows = db.execute(f"{base_query} WHERE o.status = ? ORDER BY o.created_at DESC", (status,)).fetchall()
    else:
        rows = db.execute(f"{base_query} ORDER BY o.created_at DESC").fetchall()
    return [dict(row) for row in rows]


@router.post("/orders", status_code=201)
def create_order(
    body: NewOrderRequest,
    session: dict = Depends(require_session),
    _csrf: None = Depends(require_csrf),
    db: sqlite3.Connection = Depends(get_db),
):
    garment_type = clean_text(body.garment_type, 80)
    if not garment_type:
        raise HTTPException(status_code=400, detail="Garment type is required")
    if not is_valid_price(body.price):
        raise HTTPException(status_code=400, detail="Enter a valid price")
    if not is_valid_date(body.delivery_date):
        raise HTTPException(status_code=400, detail="Enter a valid delivery date")

    customer = db.execute("SELECT customer_id FROM customers WHERE customer_id = ?", (body.customer_id,)).fetchone()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    photo_url = clean_text(body.fabric_photo_url, 300)
    cursor = db.execute(
        """INSERT INTO orders (customer_id, garment_type, fabric_photo_url, price, delivery_date, status)
           VALUES (?, ?, ?, ?, ?, 'Cut')""",
        (body.customer_id, garment_type, photo_url, float(body.price), body.delivery_date),
    )
    db.commit()
    row = db.execute("SELECT * FROM orders WHERE order_id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


@router.patch("/orders/{order_id}")
def update_order_status(
    order_id: int,
    body: UpdateOrderStatusRequest,
    session: dict = Depends(require_session),
    _csrf: None = Depends(require_csrf),
    db: sqlite3.Connection = Depends(get_db),
):
    if body.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")

    order = db.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Not found")

    if body.status == "Delivered" and order["status"] != "Delivered":
        _mark_delivered_and_flag_followup(db, order_id, order["customer_id"])
    else:
        db.execute("UPDATE orders SET status = ? WHERE order_id = ?", (body.status, order_id))
        db.commit()

    row = db.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    return dict(row)


def _mark_delivered_and_flag_followup(db: sqlite3.Connection, order_id: int, customer_id: int) -> None:
    """Delivering an order quietly opens a follow-up — this is the core
    'the relationship doesn't end at pickup' behaviour of the app."""
    db.execute(
        "UPDATE orders SET status = 'Delivered', delivered_at = datetime('now') WHERE order_id = ?",
        (order_id,),
    )
    db.execute(
        "INSERT INTO followups (customer_id, occasion_tag, status) VALUES (?, 'General', 'pending')",
        (customer_id,),
    )
    db.execute("UPDATE customers SET last_visit_date = date('now') WHERE customer_id = ?", (customer_id,))
    db.commit()


@router.get("/orders/{order_id}/payments")
def list_payments(order_id: int, session: dict = Depends(require_session), db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute(
        "SELECT * FROM payments WHERE order_id = ? ORDER BY payment_date DESC", (order_id,)
    ).fetchall()
    return [dict(row) for row in rows]


@router.post("/orders/{order_id}/payments", status_code=201)
def add_payment(
    order_id: int,
    body: NewPaymentRequest,
    session: dict = Depends(require_session),
    _csrf: None = Depends(require_csrf),
    db: sqlite3.Connection = Depends(get_db),
):
    if not is_valid_price(body.amount):
        raise HTTPException(status_code=400, detail="Enter a valid amount")
    if body.type not in VALID_PAYMENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid payment type")
    if body.method and body.method not in VALID_PAYMENT_METHODS:
        raise HTTPException(status_code=400, detail="Invalid payment method")

    order = db.execute("SELECT order_id FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    cursor = db.execute(
        "INSERT INTO payments (order_id, amount, type, method) VALUES (?, ?, ?, ?)",
        (order_id, float(body.amount), body.type, body.method),
    )
    db.commit()
    row = db.execute("SELECT * FROM payments WHERE payment_id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)
