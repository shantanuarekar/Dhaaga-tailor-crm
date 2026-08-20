import sqlite3
from datetime import date

from fastapi import APIRouter, Depends

from backend.deps import get_db, require_session

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard")
def get_dashboard(session: dict = Depends(require_session), db: sqlite3.Connection = Depends(get_db)):
    today = date.today().isoformat()

    due_today = db.execute(
        "SELECT COUNT(*) AS n FROM orders WHERE delivery_date = ? AND status != 'Delivered'", (today,)
    ).fetchone()["n"]
    pending_followups = db.execute(
        "SELECT COUNT(*) AS n FROM followups WHERE status = 'pending'"
    ).fetchone()["n"]
    active_orders = db.execute(
        "SELECT COUNT(*) AS n FROM orders WHERE status != 'Delivered'"
    ).fetchone()["n"]
    total_customers = db.execute("SELECT COUNT(*) AS n FROM customers").fetchone()["n"]

    due_list = db.execute(
        """SELECT o.order_id, o.garment_type, o.delivery_date, o.status, c.name, c.phone
           FROM orders o JOIN customers c ON c.customer_id = o.customer_id
           WHERE o.status != 'Delivered'
           ORDER BY o.delivery_date ASC LIMIT 10"""
    ).fetchall()

    return {
        "dueToday": due_today,
        "pendingFollowups": pending_followups,
        "activeOrders": active_orders,
        "totalCustomers": total_customers,
        "dueList": [dict(row) for row in due_list],
    }
