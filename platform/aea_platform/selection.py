from __future__ import annotations

# T-04 MVP customization boundary (ADR-006). Only an eligible size and a physical
# card message are MVP options; flower type, colour, ribbon, free-form
# composition, and stored-value gift cards remain Future (FR-003).
CARD_MESSAGE_MAX_LENGTH = 280
SIZE_MAX_LENGTH = 40
ALLOWED_OPTION_KEYS = ("size", "card_message")


class SelectionValidationError(ValueError):
    """A T-04 selection option violates the ADR-006 MVP contract."""


def normalize_card_message(value):
    """Normalize the optional physical card message (ADR-006).

    Optional: ``None`` or a blank string means no card message and returns
    ``None``. Otherwise the message is plain text: trimmed, control characters
    other than newline and tab are rejected, and at most
    ``CARD_MESSAGE_MAX_LENGTH`` characters. The card and its message are order
    content fulfilled with the product, never payment or stored value.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        raise SelectionValidationError("card message must be text")
    text = value.strip()
    if not text:
        return None
    if len(text) > CARD_MESSAGE_MAX_LENGTH:
        raise SelectionValidationError("card message exceeds the maximum length")
    if any(ord(character) < 32 and character not in "\n\t" for character in text):
        raise SelectionValidationError("card message contains unsupported characters")
    return text


def normalize_size(value):
    """Normalize the optional eligible catalog size token.

    Authoritative size eligibility against catalog and inventory is FR-013; this
    validates only the contract field shape (optional, bounded, control-free) so
    it is distinct from card-message content.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        raise SelectionValidationError("size must be text")
    text = value.strip()
    if not text:
        return None
    if len(text) > SIZE_MAX_LENGTH or any(ord(character) < 32 for character in text):
        raise SelectionValidationError("size is invalid")
    return text


def normalize_selection_options(options) -> dict:
    """Return the explicit MVP option fields, rejecting FR-003 controls.

    Only ``size`` and ``card_message`` are MVP T-04 options (ADR-006). Any other
    key (flower type, colour, ribbon, gift-card value, free-form composition) is
    rejected so Future customization cannot enter the MVP contract. Omitted or
    blank fields are dropped rather than stored as empty values.
    """
    if options is None:
        options = {}
    if not isinstance(options, dict):
        raise SelectionValidationError("options must be an object")
    unknown = set(options) - set(ALLOWED_OPTION_KEYS)
    if unknown:
        raise SelectionValidationError(f"unsupported options: {sorted(unknown)}")
    normalized: dict = {}
    size = normalize_size(options.get("size"))
    if size is not None:
        normalized["size"] = size
    card_message = normalize_card_message(options.get("card_message"))
    if card_message is not None:
        normalized["card_message"] = card_message
    return normalized
