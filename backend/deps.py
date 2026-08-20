"""
Reusable FastAPI dependencies. Routes that need a logged-in user
just add `session: dict = Depends(require_session)` to their
function signature — no repeated boilerplate per route.
"""

from fastapi import Cookie, Header, HTTPException, Request

from backend.database.connection import get_connection
from backend.rate_limit import api_limiter
from backend.security import get_session


def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def enforce_api_rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    if not api_limiter.allow(ip):
        raise HTTPException(status_code=429, detail="Too many requests — please slow down.")


def require_session(sid: str | None = Cookie(default=None)) -> dict:
    session = get_session(sid)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return session


def require_csrf(
    request: Request,
    x_csrf_token: str | None = Header(default=None),
    sid: str | None = Cookie(default=None),
) -> None:
    """Double-submit CSRF check for state-changing requests (POST/PATCH/DELETE)."""
    session = get_session(sid)
    if not session or not x_csrf_token or x_csrf_token != session["csrf_token"]:
        raise HTTPException(status_code=403, detail="Invalid or missing CSRF token")
