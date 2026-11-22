
from datetime import datetime

from .errors import ValidationError

MAX_SHORT_TEXT = 120
MAX_LONG_TEXT = 1000


def clean_text(value, field, max_length=MAX_SHORT_TEXT):
    if value is None:
        raise ValidationError(f"{field} is required.")
    text = " ".join(str(value).split())
    if not text:
        raise ValidationError(f"{field} cannot be empty.")
    if len(text) > max_length:
        raise ValidationError(f"{field} must be {max_length} characters or fewer.")
    return text


def clean_date(value):
    text = (value or "").strip()
    if not text:
        raise ValidationError("Event date is required.")
    try:
        return datetime.strptime(text, "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise ValidationError(
            "Date must use the format YYYY-MM-DD (for example 2026-12-05)."
        ) from None


def clean_record_id(value):
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValidationError("Record ID must be a whole number.") from None
    if number <= 0:
        raise ValidationError("Record ID must be greater than zero.")
    return number
