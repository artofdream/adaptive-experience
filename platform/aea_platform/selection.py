from __future__ import annotations

# T-04 selection options (ADR-006 amended for thin FR-003 and M10 Compositional Selection).
# Supports catalog size, card message, thin compositional keys (flower_type, colour, ribbon),
# and Option A Florist-Choice Palette Co-Creation (palette, safety_exclusions).
from .recommendation import REFERENCE_CATALOG

CARD_MESSAGE_MAX_LENGTH = 280
SIZE_MAX_LENGTH = 40
OPTION_TOKEN_MAX_LENGTH = 40

QUANTITY_MIN = 1
QUANTITY_MAX = 10

ALLOWED_OPTION_KEYS = (
    "size",
    "card_message",
    "flower_type",
    "colour",
    "ribbon",
    "palette",
    "safety_exclusions",
    "quantity",
)

ALLOWED_COLOURS = frozenset({"red", "pink", "white", "yellow", "purple", "mixed"})
ALLOWED_RIBBONS = frozenset({"none", "satin", "organza", "kraft"})

ALLOWED_PALETTES = frozenset({
    "pastel_romance",
    "vibrant_sunburst",
    "classic_elegant",
    "sunset_warmth",
    "white_green_sophistication",
})

ALLOWED_SAFETY_EXCLUSIONS = frozenset({
    "pet_safe_cat",
    "pet_safe_dog",
    "fragrance_free",
    "lily_free",
})


class SelectionValidationError(ValueError):
    """A T-04 selection option violates the selection contract."""


def normalize_card_message(value):
    """Normalize the optional physical card message (ADR-006)."""
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
    """Normalize the optional eligible catalog size token."""
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
    """Normalize an optional bounded option token (flower_type, colour, ribbon, palette)."""
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


def normalize_safety_exclusions(value) -> list[str]:
    """Normalize safety and allergen exclusions for M10 Florist-Choice Palette Co-Creation."""
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple, set)):
        raise SelectionValidationError("safety_exclusions must be a list or array")
    
    normalized = []
    for item in value:
        token = normalize_option_token(item, field="safety_exclusions")
        if token is not None:
            if token not in ALLOWED_SAFETY_EXCLUSIONS:
                raise SelectionValidationError(f"unsupported safety exclusion: {token}")
            if token not in normalized:
                normalized.append(token)
    return normalized


def flowers_for_product(product_id: str) -> frozenset[str]:
    """Return reference-catalog flower tags for a product id."""
    for product in REFERENCE_CATALOG:
        if product.product_id == product_id:
            return product.flowers
    raise SelectionValidationError("unknown product for flower type")


def normalize_quantity(value) -> int:
    """Normalize item selection quantity (ADR-006 / FR-003 quantity)."""
    if value is None:
        return 1
    if isinstance(value, str):
        if not value.strip().isdigit():
            raise SelectionValidationError("quantity must be a positive integer")
        value = int(value.strip())
    if not isinstance(value, int) or isinstance(value, bool):
        raise SelectionValidationError("quantity must be a positive integer")
    if value < QUANTITY_MIN or value > QUANTITY_MAX:
        raise SelectionValidationError(f"quantity must be between {QUANTITY_MIN} and {QUANTITY_MAX}")
    return value


def normalize_selection_options(options, product_id: str | None = None) -> dict:
    """Return explicit T-04 option fields, including M10 Compositional Palette keys.

    Accepts ``size``, ``card_message``, ``flower_type``, ``colour``, ``ribbon``,
    ``palette``, ``safety_exclusions``, and ``quantity``.
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

    # M10 Option A: Florist-Choice Palette & Safety Exclusions
    palette = normalize_option_token(options.get("palette"), field="palette")
    if palette is not None:
        if palette not in ALLOWED_PALETTES:
            raise SelectionValidationError("palette is not allowed")
        normalized["palette"] = palette

    safety_exclusions = normalize_safety_exclusions(options.get("safety_exclusions"))
    if safety_exclusions:
        normalized["safety_exclusions"] = safety_exclusions

    if options.get("quantity") is not None:
        quantity = normalize_quantity(options.get("quantity"))
        normalized["quantity"] = quantity

    return normalized


def normalize_selection_items(items) -> list[dict]:
    """Normalize a multi-product selection items array for cart basket selection."""
    if items is None:
        return []
    if not isinstance(items, (list, tuple)):
        raise SelectionValidationError("items must be an array")
    if len(items) > 20:
        raise SelectionValidationError("maximum 20 distinct items allowed per cart")
    normalized = []
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("product_id"), str) or not item["product_id"].strip():
            raise SelectionValidationError("item must contain product_id")
        pid = item["product_id"].strip()
        opts = item.get("options", {}) if isinstance(item.get("options"), dict) else {}
        norm_opts = normalize_selection_options(opts, product_id=pid)
        qty = item.get("quantity")
        if qty is not None:
            norm_opts["quantity"] = normalize_quantity(qty)
        normalized.append({
            "product_id": pid,
            "quantity": norm_opts.get("quantity", 1),
            "options": norm_opts,
        })
    return normalized


STEM_PRICES_CENTS = {
    "roses": 450,
    "lilies": 650,
    "carnations": 300,
    "orchids": 850,
    "eucalyptus": 250,
}

def calculate_stem_composition_price(stems: dict) -> int:
    """Calculate dynamic price in cents for custom stem-by-stem bouquet composition (GAP-V01)."""
    if not isinstance(stems, dict):
        return 0
    total = 0
    for stem_type, count in stems.items():
        if stem_type in STEM_PRICES_CENTS and isinstance(count, int) and count > 0:
            total += STEM_PRICES_CENTS[stem_type] * min(count, 50)
    return total

