import sqlite3

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response

from backend.config import CSRF_COOKIE_NAME, IS_PRODUCTION, SESSION_COOKIE_NAME
from backend.deps import get_db, require_session
from backend.models.auth import ChangePasswordRequest, LoginRequest
from backend.rate_limit import login_limiter
from backend.security import (
    SESSION_TTL_SECONDS,
    create_session,
    destroy_session,
    hash_password,
    verify_password,
)
from backend.validators import clean_text

router = APIRouter(prefix="/api", tags=["auth"])


def _set_auth_cookies(response: Response, sid: str, csrf_token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE_NAME, sid, max_age=SESSION_TTL_SECONDS,
        httponly=True, samesite="lax", secure=IS_PRODUCTION,
    )
    response.set_cookie(
        CSRF_COOKIE_NAME, csrf_token, max_age=SESSION_TTL_SECONDS,
        httponly=False, samesite="lax", secure=IS_PRODUCTION,
    )


@router.post("/login")
def login(body: LoginRequest, request: Request, response: Response, db: sqlite3.Connection = Depends(get_db)):
    ip = request.client.host if request.client else "unknown"
    if not login_limiter.allow(ip):
        raise HTTPException(status_code=429, detail="Too many login attempts — try again later.")

    username = clean_text(body.username, 60)
    if not username or not body.password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user or not verify_password(body.password, user["password_hash"], user["password_salt"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    sid, csrf_token = create_session(user["user_id"])
    _set_auth_cookies(response, sid, csrf_token)
    return {"ok": True, "username": user["username"], "displayName": user["display_name"]}


@router.post("/logout")
def logout(response: Response, sid: str | None = Cookie(default=None)):
    destroy_session(sid)
    response.delete_cookie(SESSION_COOKIE_NAME)
    response.delete_cookie(CSRF_COOKIE_NAME)
    return {"ok": True}


@router.get("/me")
def me(session: dict = Depends(require_session), db: sqlite3.Connection = Depends(get_db)):
    user = db.execute(
        "SELECT username, display_name FROM users WHERE user_id = ?", (session["user_id"],)
    ).fetchone()
    return {"username": user["username"], "displayName": user["display_name"], "csrfToken": session["csrf_token"]}


@router.post("/change-password")
def change_password(
    body: ChangePasswordRequest,
    session: dict = Depends(require_session),
    db: sqlite3.Connection = Depends(get_db),
):
    if len(body.newPassword) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")

    user = db.execute("SELECT * FROM users WHERE user_id = ?", (session["user_id"],)).fetchone()
    if not verify_password(body.currentPassword, user["password_hash"], user["password_salt"]):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    new_hash, new_salt = hash_password(body.newPassword)
    db.execute(
        "UPDATE users SET password_hash = ?, password_salt = ? WHERE user_id = ?",
        (new_hash, new_salt, user["user_id"]),
    )
    db.commit()
    return {"ok": True}
