import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from backend.deps import get_db, require_csrf, require_session
from backend.models.customer import MeasurementsRequest, NewCustomerRequest
from backend.validators import clean_text, is_valid_measurement, is_valid_phone

router = APIRouter(prefix="/api", tags=["customers"])


@router.get("/customers")
def list_customers(search: str | None = None, session: dict = Depends(require_session), db: sqlite3.Connection = Depends(get_db)):
    query = clean_text(search, 100) or ""
    if query:
        like = f"%{query}%"
        rows = db.execute(
            "SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? ORDER BY name", (like, like)
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM customers ORDER BY name").fetchall()
    return [dict(row) for row in rows]


@router.post("/customers", status_code=201)
def create_customer(
    body: NewCustomerRequest,
    session: dict = Depends(require_session),
    _csrf: None = Depends(require_csrf),
    db: sqlite3.Connection = Depends(get_db),
):
    name = clean_text(body.name, 100)
    phone = clean_text(body.phone, 10)

    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    if not is_valid_phone(phone or ""):
        raise HTTPException(status_code=400, detail="Enter a valid 10-digit Indian mobile number")

    try:
        cursor = db.execute(
            "INSERT INTO customers (name, phone, referred_by, last_visit_date) VALUES (?, ?, ?, date('now'))",
            (name, phone, body.referred_by),
        )
        db.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Phone number already exists")

    row = db.execute("SELECT * FROM customers WHERE customer_id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


@router.get("/customers/{customer_id}")
def get_customer(customer_id: int, session: dict = Depends(require_session), db: sqlite3.Connection = Depends(get_db)):
    customer = db.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,)).fetchone()
    if not customer:
        raise HTTPException(status_code=404, detail="Not found")

    measurements = db.execute(
        "SELECT * FROM measurements WHERE customer_id = ? ORDER BY updated_at DESC LIMIT 1", (customer_id,)
    ).fetchone()
    orders = db.execute(
        "SELECT * FROM orders WHERE customer_id = ? ORDER BY created_at DESC", (customer_id,)
    ).fetchall()

    result = dict(customer)
    result["measurements"] = dict(measurements) if measurements else None
    result["orders"] = [dict(o) for o in orders]
    return result


@router.post("/customers/{customer_id}/measurements", status_code=201)
def add_measurements(
    customer_id: int,
    body: MeasurementsRequest,
    session: dict = Depends(require_session),
    _csrf: None = Depends(require_csrf),
    db: sqlite3.Connection = Depends(get_db),
):
    customer = db.execute("SELECT customer_id FROM customers WHERE customer_id = ?", (customer_id,)).fetchone()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    fields = [body.chest, body.waist, body.hip, body.shoulder, body.sleeve_length, body.length]
    if not all(is_valid_measurement(v) for v in fields):
        raise HTTPException(status_code=400, detail="Measurements must be reasonable positive numbers")

    notes = clean_text(body.notes, 500)
    cursor = db.execute(
        """INSERT INTO measurements
           (customer_id, chest, waist, hip, shoulder, sleeve_length, length, notes, voice_note_url)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (customer_id, body.chest or None, body.waist or None, body.hip or None,
         body.shoulder or None, body.sleeve_length or None, body.length or None,
         notes, body.voice_note_url),
    )
    db.commit()
    row = db.execute("SELECT * FROM measurements WHERE measurement_id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


@router.get("/customers/{customer_id}/referrals")
def get_referrals(customer_id: int, session: dict = Depends(require_session), db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute(
        "SELECT customer_id, name, phone, created_at FROM customers WHERE referred_by = ?", (customer_id,)
    ).fetchall()
    return [dict(row) for row in rows]
