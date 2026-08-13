from __future__ import annotations

from .recommendation import REFERENCE_CATALOG

# Reference itemized pricing for the FR-018 Order Summary (T-06). This is a
# deterministic reference model, not an authoritative pricing engine: product
# prices come from the reference catalog, delivery is a flat reference fee, and
# the physical card message is included in the product price (ADR-006 / #122).
CURRENCY = "USD"
REFERENCE_DELIVERY_FEE = 12.0


class PricingService:
    """Compute the itemized order summary from the current decisions (FR-018).

    Derived projection: the summary is recomputed from `decisions.product` (with
    its size/card options) and `decisions.delivery`, mirroring how recommendations
    regenerate. It is not stored and publishes nothing; the `order.summary.updated`
    event and authoritative pricing belong to the checkout flow (M5, #38).
    """

    def __init__(self, catalog=None, *, delivery_fee: float = REFERENCE_DELIVERY_FEE):
        self.prices = {product.product_id: product.price
                       for product in (catalog if catalog is not None else REFERENCE_CATALOG)}
        self.delivery_fee = float(delivery_fee)

    def summarize(self, decisions) -> dict | None:
        if not isinstance(decisions, dict):
            return None
        product = decisions.get("product")
        if not isinstance(product, dict) or not isinstance(product.get("product_id"), str):
            return None
        base = self.prices.get(product["product_id"])
        if base is None:
            # Unknown product; authoritative catalog owns eligibility.
            return None
        charges = [{"label": "product", "product_id": product["product_id"],
                    "amount": round(float(base), 2)}]
        options = product.get("options")
        if isinstance(options, dict) and options.get("card_message"):
            charges.append({"label": "card_message", "amount": 0.0})
        delivery = decisions.get("delivery")
        if isinstance(delivery, dict) and delivery.get("destination_reference"):
            charges.append({"label": "delivery", "amount": round(self.delivery_fee, 2)})
        total = round(sum(charge["amount"] for charge in charges), 2)
        return {"currency": CURRENCY, "itemized_charges": charges, "total": total}
