"""
Small, focused validation functions. Kept separate from the Pydantic
models because a couple of these (phone format, date format) are
domain-specific rules, not just "is this a string".
"""

import re
from datetime import datetime

PHONE_PATTERN = re.compile(r"^[6-9]\d{9}$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

VALID_STATUSES = ["Cut", "Stitching", "Ready", "Delivered"]
VALID_PAYMENT_TYPES = ["advance", "balance"]
VALID_PAYMENT_METHODS = ["cash", "upi", "card"]


def is_valid_phone(phone: str) -> bool:
    return bool(phone) and bool(PHONE_PATTERN.match(phone.strip()))


def is_valid_price(price) -> bool:
    try:
        value = float(price)
    except (TypeError, ValueError):
        return False
    return 0 < value < 10_000_000


def is_valid_date(date_str: str | None) -> bool:
    if not date_str:
        return True  # optional field
    if not DATE_PATTERN.match(date_str):
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_measurement(value) -> bool:
    if value is None or value == "":
        return True
    try:
        n = float(value)
    except (TypeError, ValueError):
        return False
    return 0 <= n < 1000


def clean_text(text: str | None, max_len: int) -> str | None:
    if text is None:
        return None
    trimmed = text.strip()[:max_len]
    return trimmed or None
