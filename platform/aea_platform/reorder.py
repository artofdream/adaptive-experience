"""Reorder & Prior Order Recall Service (FR-008 / Milestone M8).

Implements durable same-browser prior-order retrieval, reorder item resolution,
and modify-before-reorder payload preparation without requiring customer login.
Coherent with ADR-005, ADR-009, ADR-013, and FR-008.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PriorOrderItem:
    product_id: str
    size: str
    card_message: Optional[str] = None
    customizations: Dict[str, str] = field(default_factory=dict)
    quantity: int = 1
    price_cents: int = 0


@dataclass
class PriorOrderSummary:
    order_id: str
    browser_token: str
    items: List[PriorOrderItem]
    total_cents: int
    created_at_iso: str
    delivery_postcode: str


class ReorderService:
    """Service managing prior-order recall and modify-before-reorder resolution."""

    def __init__(self, order_store: Optional[Dict[str, List[PriorOrderSummary]]] = None):
        self.store = order_store if order_store is not None else {}

    def get_prior_orders(self, browser_token: str) -> List[PriorOrderSummary]:
        """Fetch prior orders associated with a durable browser token."""
        return self.store.get(browser_token, [])

    def prepare_reorder(self, browser_token: str, order_id: str, modify_items: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare a workspace reorder payload, optionally merging modify-before-reorder changes."""
        orders = self.get_prior_orders(browser_token)
        target_order = next((o for o in orders if o.order_id == order_id), None)

        if not target_order:
            raise ValueError(f"Prior order {order_id} not found for browser token")

        reorder_items = []
        for item in target_order.items:
            item_data = {
                "product_id": item.product_id,
                "size": item.size,
                "card_message": item.card_message,
                "customizations": dict(item.customizations),
                "quantity": item.quantity,
            }
            # Apply modifications if specified for product
            if modify_items and item.product_id in modify_items:
                mod = modify_items[item.product_id]
                if "size" in mod:
                    item_data["size"] = mod["size"]
                if "card_message" in mod:
                    item_data["card_message"] = mod["card_message"]
                if "customizations" in mod:
                    item_data["customizations"].update(mod["customizations"])
                if "quantity" in mod:
                    item_data["quantity"] = mod["quantity"]

            reorder_items.append(item_data)

        return {
            "source_order_id": order_id,
            "browser_token": browser_token,
            "reorder_items": reorder_items,
            "modified": bool(modify_items),
        }
