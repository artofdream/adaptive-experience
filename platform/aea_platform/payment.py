from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional, Protocol


class PaymentValidationError(ValueError):
    """The payment reference is not an acceptable opaque token."""


@dataclass(frozen=True)
class PaymentOutcome:
    authorized: bool
    decline_code: Optional[str] = None
    transaction_id: Optional[str] = None
    event_type: Optional[str] = None


def normalize_payment_reference(value: Any) -> str:
    """Validate an opaque payment token (FR-019 / NFR-013 / NFR-017).

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

    Supports stripe-mock token conventions (tok_visa, tok_chargeDeclined, tok_visa_debit)
    and produces versioned payment bus events (payment.processed.v1 / payment.failed.v1).
    """

    def authorize(self, *, payment_reference: str, total: float) -> PaymentOutcome:
        reference = normalize_payment_reference(payment_reference)
        if isinstance(total, bool) or not isinstance(total, (int, float)) or total <= 0:
            return PaymentOutcome(False, "invalid_total")
        
        # Decline simulation tokens (stripe-mock style or decline- prefix)
        if reference.startswith("decline-"):
            return PaymentOutcome(
                authorized=False,
                decline_code="declined",
                event_type="payment.failed.v1"
            )
        if reference in ("tok_chargeDeclined", "tok_cardDeclineInsufficientFunds"):
            return PaymentOutcome(
                authorized=False,
                decline_code="card_declined",
                event_type="payment.failed.v1"
            )
        
        # Successful payment simulation tokens (tok_visa, tok_visa_debit, pay_token_*)
        txn_id = f"txn_sim_{hash(reference + str(total)) & 0xFFFFFFFF:08x}"
        return PaymentOutcome(
            authorized=True,
            decline_code=None,
            transaction_id=txn_id,
            event_type="payment.processed.v1"
        )


class PaymentSimulationEngine:
    """Open-Source Payment Simulator orchestrator compatible with stripe-mock API conventions."""

    def __init__(self, authority: Optional[PaymentAuthority] = None):
        self.authority = authority if authority is not None else ReferencePaymentAuthority()

    def process_checkout_payment(
        self,
        order_id: str,
        payment_reference: str,
        amount_cents: int,
        currency: str = "AUD"
    ) -> Dict[str, Any]:
        """Process tokenized payment and return structured bus envelope data."""
        total_dollars = amount_cents / 100.0
        outcome = self.authority.authorize(payment_reference=payment_reference, total=total_dollars)

        if outcome.authorized:
            return {
                "status": "succeeded",
                "order_id": order_id,
                "transaction_id": outcome.transaction_id,
                "amount_cents": amount_cents,
                "currency": currency,
                "event_type": outcome.event_type,
                "error": None,
            }
        else:
            return {
                "status": "failed",
                "order_id": order_id,
                "transaction_id": None,
                "amount_cents": amount_cents,
                "currency": currency,
                "event_type": outcome.event_type,
                "error": outcome.decline_code or "declined",
            }
