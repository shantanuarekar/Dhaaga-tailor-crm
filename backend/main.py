"""
Application entrypoint. Run with: uvicorn backend.main:app
(or just `python run.py` from the project root — see README).
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.config import FRONTEND_DIR, IS_PRODUCTION
from backend.database.connection import get_connection, is_new_database, run_schema
from backend.database.seed import seed_admin_user, seed_sample_data
from backend.deps import enforce_api_rate_limit
from backend.routes import auth, customers, dashboard, followups, orders

app = FastAPI(title="Dhaaga CRM")


@app.exception_handler(HTTPException)
async def as_error_field(request: Request, exc: HTTPException):
    """The frontend expects {"error": "..."}; FastAPI's default is {"detail": "..."}."""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.on_event("startup")
def initialize_database() -> None:
    first_run = is_new_database()
    conn = get_connection()
    run_schema(conn)
    if first_run:
        seed_admin_user(conn)
        seed_sample_data(conn)
    conn.close()


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; script-src 'self'; connect-src 'self'"
    )
    if IS_PRODUCTION:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.middleware("http")
async def rate_limit_api(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        try:
            enforce_api_rate_limit(request)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
    return await call_next(request)


# API routers — must be registered before the static file catch-all below
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(followups.router)

# Serves index.html, style.css, and the js/ modules — this must come last
# so it doesn't shadow the /api/* routes above.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
