from __future__ import annotations

from datetime import datetime

# FR-014 delivery scheduling. Recipient details are reference-only: the delivery
# decision and its event carry an opaque `destination_reference`, never raw
# recipient name/address/contact (PayloadPrivacyGuard forbids those in envelopes).
ALLOWED_DELIVERY_KEYS = ("timing", "destination_reference")
ALLOWED_TIMING_KEYS = ("date", "window")
ALLOWED_WINDOWS = ("morning", "afternoon", "evening")
DESTINATION_REFERENCE_MAX_LENGTH = 200


class DeliveryValidationError(ValueError):
    """A delivery-details field violates the FR-014 contract."""


def normalize_delivery_details(details) -> dict:
    """Validate and normalize the FR-014 delivery decision.

    Accepts exactly ``timing`` (date + delivery window) and an opaque
    ``destination_reference``. Any other key - including raw recipient fields -
    is rejected, so personally identifiable recipient data never enters
    experience state or the governed event.
    """
    if not isinstance(details, dict):
        raise DeliveryValidationError("delivery details must be an object")
    unknown = set(details) - set(ALLOWED_DELIVERY_KEYS)
    if unknown:
        raise DeliveryValidationError(f"unsupported delivery fields: {sorted(unknown)}")
    return {
        "destination_reference": _reference(details.get("destination_reference")),
        "timing": _timing(details.get("timing")),
    }


def _reference(value) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DeliveryValidationError("destination reference is required")
    text = value.strip()
    if len(text) > DESTINATION_REFERENCE_MAX_LENGTH or any(ord(c) < 32 for c in text):
        raise DeliveryValidationError("destination reference is invalid")
    return text


def _timing(value) -> dict:
    if not isinstance(value, dict):
        raise DeliveryValidationError("timing is required")
    unknown = set(value) - set(ALLOWED_TIMING_KEYS)
    if unknown:
        raise DeliveryValidationError(f"unsupported timing fields: {sorted(unknown)}")
    date = value.get("date")
    if not isinstance(date, str) or not _is_iso_date(date):
        raise DeliveryValidationError("delivery date is invalid")
    window = value.get("window")
    if window not in ALLOWED_WINDOWS:
        raise DeliveryValidationError("delivery window is invalid")
    return {"date": date, "window": window}


def _is_iso_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False
