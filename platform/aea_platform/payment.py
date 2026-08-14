from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class PaymentValidationError(ValueError):
    """The payment reference is not an acceptable opaque token."""


@dataclass(frozen=True)
class PaymentOutcome:
    authorized: bool
    decline_code: str | None = None


def normalize_payment_reference(value) -> str:
    """Validate an opaque payment token (FR-019 / NFR-013).

    A payment reference is a token for a payment method held in a PCI-scoped
    vault. Raw card data must never reach the platform, so a value that looks like
    a card number (12-19 bare digits) is rejected; the guard also forbids raw card
    fields in envelopes.
    """
    if not isinstance(value, str) or not value.strip():
        raise PaymentValidationError("payment reference is required")
    text = value.strip()
    if len(text) > 200 or any(ord(character) < 32 for character in text):
        raise PaymentValidationError("payment reference is invalid")
    bare = text.replace(" ", "").replace("-", "")
    if bare.isdigit() and 12 <= len(bare) <= 19:
        raise PaymentValidationError("raw card numbers are prohibited; use a vault token")
    return text


class PaymentAuthority(Protocol):
    def authorize(self, *, payment_reference: str, total: float) -> PaymentOutcome: ...


class ReferencePaymentAuthority:
    """Deterministic reference authorization against an opaque payment token.

    Not a real gateway. It authorizes any valid opaque `payment_reference` for a
    positive total; a reference beginning with ``decline-`` is declined so the
    decline path is testable. Call site is the payment consumer
    (``PaymentCheckoutHandler``), not the checkout HTTP path (#148).
    """

    def authorize(self, *, payment_reference: str, total: float) -> PaymentOutcome:
        reference = normalize_payment_reference(payment_reference)
        if isinstance(total, bool) or not isinstance(total, (int, float)) or total <= 0:
            return PaymentOutcome(False, "invalid_total")
        if reference.startswith("decline-"):
            return PaymentOutcome(False, "declined")
        return PaymentOutcome(True, None)
