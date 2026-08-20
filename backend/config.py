"""
Central place for settings that would otherwise be magic numbers
scattered across the codebase.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

IS_PRODUCTION = os.environ.get("ENVIRONMENT") == "production"
PORT = int(os.environ.get("PORT", 8000))

SESSION_COOKIE_NAME = "sid"
CSRF_COOKIE_NAME = "csrf"
