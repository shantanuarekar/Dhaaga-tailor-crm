import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from backend.deps import get_db, require_csrf, require_session
from backend.models.followup import UpdateFollowupRequest

router = APIRouter(prefix="/api", tags=["followups"])

VALID_FOLLOWUP_STATUSES = ["pending", "contacted", "replied"]


@router.get("/followups")
def list_followups(session: dict = Depends(require_session), db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute(
        """SELECT f.*, c.name, c.phone
           FROM followups f JOIN customers c ON c.customer_id = f.customer_id
           WHERE f.status = 'pending'
           ORDER BY f.flagged_at ASC"""
    ).fetchall()
    return [dict(row) for row in rows]


@router.patch("/followups/{followup_id}")
def update_followup(
    followup_id: int,
    body: UpdateFollowupRequest,
    session: dict = Depends(require_session),
    _csrf: None = Depends(require_csrf),
    db: sqlite3.Connection = Depends(get_db),
):
    if body.status not in VALID_FOLLOWUP_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")

    db.execute(
        "UPDATE followups SET status = ?, last_contacted = datetime('now') WHERE followup_id = ?",
        (body.status, followup_id),
    )
    db.commit()
    row = db.execute("SELECT * FROM followups WHERE followup_id = ?", (followup_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return dict(row)
