from __future__ import annotations

# T-04 selection options (ADR-006 amended for thin FR-003). Size and card message
# remain MVP basics; flower_type, colour, and ribbon are accepted thin
# compositional keys. Free-form bouquet composition and stored-value gift cards
# remain out of scope.
from .recommendation import REFERENCE_CATALOG

CARD_MESSAGE_MAX_LENGTH = 280
SIZE_MAX_LENGTH = 40
OPTION_TOKEN_MAX_LENGTH = 40
ALLOWED_OPTION_KEYS = ("size", "card_message", "flower_type", "colour", "ribbon")
ALLOWED_COLOURS = frozenset({"red", "pink", "white", "yellow", "purple", "mixed"})
ALLOWED_RIBBONS = frozenset({"none", "satin", "organza", "kraft"})


class SelectionValidationError(ValueError):
    """A T-04 selection option violates the selection contract."""


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


def normalize_option_token(value, *, field: str):
    """Normalize an optional bounded option token (flower_type, colour, ribbon)."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise SelectionValidationError(f"{field} must be text")
    text = value.strip().lower()
    if not text:
        return None
    if len(text) > OPTION_TOKEN_MAX_LENGTH or any(ord(character) < 32 for character in text):
        raise SelectionValidationError(f"{field} is invalid")
    return text


def flowers_for_product(product_id: str) -> frozenset[str]:
    """Return reference-catalog flower tags for a product id."""
    for product in REFERENCE_CATALOG:
        if product.product_id == product_id:
            return product.flowers
    raise SelectionValidationError("unknown product for flower type")


def normalize_selection_options(options, product_id: str | None = None) -> dict:
    """Return explicit T-04 option fields, including thin FR-003 keys.

    Accepts ``size``, ``card_message``, ``flower_type``, ``colour``, and
    ``ribbon``. ``flower_type`` must match the selected product's reference
    catalog flower tags when provided. ``colour`` and ``ribbon`` use fixed
    reference vocabularies until a Catalog SoT exists. Stored-value gift cards
    and other unknown keys are rejected. Omitted or blank fields are dropped.
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

    flower_type = normalize_option_token(options.get("flower_type"), field="flower_type")
    if flower_type is not None:
        if not isinstance(product_id, str) or not product_id.strip():
            raise SelectionValidationError("flower type requires a product")
        allowed = flowers_for_product(product_id.strip())
        if flower_type not in allowed:
            raise SelectionValidationError("flower type is not eligible for product")
        normalized["flower_type"] = flower_type

    colour = normalize_option_token(options.get("colour"), field="colour")
    if colour is not None:
        if colour not in ALLOWED_COLOURS:
            raise SelectionValidationError("colour is not allowed")
        normalized["colour"] = colour

    ribbon = normalize_option_token(options.get("ribbon"), field="ribbon")
    if ribbon is not None:
        if ribbon not in ALLOWED_RIBBONS:
            raise SelectionValidationError("ribbon is not allowed")
        normalized["ribbon"] = ribbon

    return normalized
