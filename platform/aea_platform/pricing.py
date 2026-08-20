from __future__ import annotations

from .recommendation import REFERENCE_CATALOG

# Reference itemized pricing for the FR-018 Order Summary (T-06). This is a
# deterministic reference model, not an authoritative pricing engine: product
# prices come from the reference catalog, delivery is a flat reference fee, and
# thin FR-003 / card message customization carries no surcharge (ADR-006 / T-04).
#
# Once a known product is selected, the summary always emits the FR-018
# categories: product, customization, delivery (when a destination exists),
# tax, discount, and total. Reference tax and discount amounts are 0.00 until a
# pricing authority supplies rates or promotions.
CURRENCY = "USD"
REFERENCE_DELIVERY_FEE = 12.0
REFERENCE_TAX_RATE = 0.0
REFERENCE_DISCOUNT_AMOUNT = 0.0
REFERENCE_CUSTOMIZATION_AMOUNT = 0.0

FR018_LABELS = ("product", "customization", "delivery", "tax", "discount")


class PricingService:
    """Compute the itemized order summary from the current decisions (FR-018).

    Derived projection: the summary is recomputed from `decisions.product` (with
    its size/card/thin options) and `decisions.delivery`, mirroring how
    recommendations regenerate. It is not stored and publishes nothing; the
    `order.summary.updated` event and authoritative pricing belong to the
    checkout flow (M5, #38).
    """

    def __init__(
        self,
        catalog=None,
        *,
        delivery_fee: float = REFERENCE_DELIVERY_FEE,
        tax_rate: float = REFERENCE_TAX_RATE,
        discount_amount: float = REFERENCE_DISCOUNT_AMOUNT,
        customization_amount: float = REFERENCE_CUSTOMIZATION_AMOUNT,
    ):
        self.prices = {
            product.product_id: product.price
            for product in (catalog if catalog is not None else REFERENCE_CATALOG)
        }
        self.delivery_fee = float(delivery_fee)
        self.tax_rate = float(tax_rate)
        self.discount_amount = float(discount_amount)
        self.customization_amount = float(customization_amount)

    def summarize(self, decisions) -> dict | None:
        if not isinstance(decisions, dict):
            return None
        items = decisions.get("items")
        product = decisions.get("product")
        if not items and isinstance(product, dict) and isinstance(product.get("items"), list):
            items = product["items"]

        item_list = []
        if isinstance(items, list) and len(items) > 0:
            item_list = [i for i in items if isinstance(i, dict) and isinstance(i.get("product_id"), str)]
        elif isinstance(product, dict) and isinstance(product.get("product_id"), str):
            item_list = [product]

        if not item_list:
            return None

        total_product_amount = 0.0
        charges = []

        for item in item_list:
            pid = item.get("product_id")
            base = self.prices.get(pid)
            if base is None:
                continue
            options = item.get("options") if isinstance(item.get("options"), dict) else {}
            raw_qty = item.get("quantity", options.get("quantity", 1))
            try:
                qty = int(raw_qty)
                if qty < 1:
                    qty = 1
            except (ValueError, TypeError):
                qty = 1

            line_amount = round(float(base) * qty, 2)
            total_product_amount += line_amount
            charges.append({
                "label": "product",
                "product_id": pid,
                "quantity": qty,
                "unit_price": round(float(base), 2),
                "amount": line_amount,
            })

        if not charges:
            return None

        customization_amount = round(self.customization_amount, 2)
        charges.append({"label": "customization", "amount": customization_amount})

        delivery_amount = 0.0
        delivery = decisions.get("delivery")
        if isinstance(delivery, dict) and delivery.get("destination_reference"):
            delivery_amount = round(self.delivery_fee, 2)
            charges.append({"label": "delivery", "amount": delivery_amount})

        taxable = total_product_amount + customization_amount + delivery_amount
        tax_amount = round(taxable * self.tax_rate, 2)
        discount_amount = round(self.discount_amount, 2)
        charges.append({"label": "tax", "amount": tax_amount})
        charges.append({"label": "discount", "amount": discount_amount})

        total = round(taxable + tax_amount - discount_amount, 2)
        return {"currency": CURRENCY, "itemized_charges": charges, "total": total}
