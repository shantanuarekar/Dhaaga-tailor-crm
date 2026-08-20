"""
Everything auth-related that isn't a route: password hashing,
the in-memory session store, and CSRF token creation.

Passwords are hashed with scrypt (via Python's hashlib), which is
memory-hard and a good default for a project like this — no external
password-hashing library needed.
"""

import hashlib
import hmac
import secrets
import time

SESSION_TTL_SECONDS = 8 * 60 * 60  # 8 hours

# sid -> {"user_id": int, "csrf_token": str, "expires_at": float}
_sessions: dict[str, dict] = {}


def hash_password(password: str) -> tuple[str, str]:
    """Returns (hash_hex, salt_hex)."""
    salt = secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1)
    return digest.hex(), salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    digest = hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1)
    return hmac.compare_digest(digest.hex(), stored_hash)


def create_session(user_id: int) -> tuple[str, str]:
    """Returns (session_id, csrf_token)."""
    sid = secrets.token_hex(32)
    csrf_token = secrets.token_hex(32)
    _sessions[sid] = {
        "user_id": user_id,
        "csrf_token": csrf_token,
        "expires_at": time.time() + SESSION_TTL_SECONDS,
    }
    return sid, csrf_token


def get_session(sid: str | None) -> dict | None:
    if not sid or sid not in _sessions:
        return None
    session = _sessions[sid]
    if session["expires_at"] < time.time():
        del _sessions[sid]
        return None
    return session


def destroy_session(sid: str | None) -> None:
    if sid in _sessions:
        del _sessions[sid]


def cleanup_expired_sessions() -> None:
    now = time.time()
    expired = [sid for sid, s in _sessions.items() if s["expires_at"] < now]
    for sid in expired:
        del _sessions[sid]
