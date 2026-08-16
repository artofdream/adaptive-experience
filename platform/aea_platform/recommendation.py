from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Sequence


class RecommendationValidationError(ValueError):
    pass


@dataclass(frozen=True)
class CatalogProduct:
    product_id: str
    price: float
    occasions: frozenset[str]
    styles: frozenset[str]
    flowers: frozenset[str]


@dataclass(frozen=True)
class RecommendationReady:
    message_id: str
    context_version: int
    eligible_product_ids: list[str]
    ranking: list[dict]


# Deterministic local catalog for FR-007 ranking tests (not a Catalog SoT).
REFERENCE_CATALOG: tuple[CatalogProduct, ...] = (
    CatalogProduct(
        "pink-flower-vase",
        125.0,
        frozenset({"baby shower", "birthday"}),
        frozenset({"bright", "soft"}),
        frozenset({"roses", "mixed"}),
    ),
    CatalogProduct(
        "lilac-bouquet",
        95.0,
        frozenset({"birthday", "thank you"}),
        frozenset({"soft", "classic"}),
        frozenset({"lilac", "mixed"}),
    ),
    CatalogProduct(
        "classic-rose-dozen",
        70.0,
        frozenset({"birthday", "anniversary", "romance"}),
        frozenset({"classic", "romantic"}),
        frozenset({"roses"}),
    ),
    CatalogProduct(
        "budget-mixed-bunch",
        35.0,
        frozenset({"thank you", "birthday", "baby shower"}),
        frozenset({"bright", "casual"}),
        frozenset({"mixed", "carnations"}),
    ),
    CatalogProduct(
        "premium-orchid",
        180.0,
        frozenset({"anniversary", "congratulations"}),
        frozenset({"elegant"}),
        frozenset({"orchid"}),
    ),
)


# Modest FR-007 score bump when this session already accepted an order.
# Occasion (+3) and flower (+2) still outrank a hint-only match.
PRIOR_ORDER_HINT_SCORE = 1.5


class RecommendationService:
    """Availability-aware recommendation ranking boundary (FR-007 / NFR-006).

    Optional same-session prior-order hint (thin FR-008): if ``prior_product_lookup``
    returns a catalog product_id for the session, that SKU gets a deterministic
    score bump and wins score ties. Not AI-ranked. Not cross-session history.
    """

    def __init__(
        self,
        store,
        inventory,
        *,
        catalog: Sequence[CatalogProduct] | None = None,
        limit: int = 10,
        now: Callable[[], datetime] | None = None,
        new_id: Callable[[], uuid.UUID] | None = None,
        prior_product_lookup: Callable[[str], str | None] | None = None,
    ):
        if limit < 1 or limit > 50:
            raise ValueError("recommendation limit must be between 1 and 50")
        self.store = store
        self.inventory = inventory
        self.catalog = tuple(catalog) if catalog is not None else REFERENCE_CATALOG
        self.limit = limit
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.new_id = new_id or uuid.uuid4
        self.prior_product_lookup = prior_product_lookup

    def generate(
        self,
        *,
        session_id: str,
        observed_context_version: int,
        correlation_id: str,
        subject_reference: str,
        intent: dict,
        intent_reference: str | None = None,
    ) -> RecommendationReady:
        facets = self._intent(intent)
        if (
            not isinstance(observed_context_version, int)
            or isinstance(observed_context_version, bool)
            or observed_context_version < 0
        ):
            raise RecommendationValidationError("observed context version is invalid")
        if not isinstance(correlation_id, str) or not correlation_id.strip():
            raise RecommendationValidationError("correlation ID is required")
        if not isinstance(subject_reference, str) or not subject_reference.strip():
            raise RecommendationValidationError("subject reference is required")
        reference = (intent_reference or session_id or "").strip()
        if not reference:
            raise RecommendationValidationError("intent reference is required")

        prior_product_id = self._prior_product_id(session_id)
        scored = self._rank(facets, prior_product_id=prior_product_id)
        product_ids = [product.product_id for product, _score in scored]
        availability = {}
        if product_ids:
            validation = self.inventory.validate(
                session_id=session_id,
                product_ids=product_ids,
                observed_context_version=observed_context_version,
                correlation_id=correlation_id.strip(),
                subject_reference=subject_reference.strip(),
                purpose="recommendation",
            )
            availability = validation.availability

        eligible: list[str] = []
        ranking: list[dict] = []
        for product, score in scored:
            status = availability.get(product.product_id, {}).get("status")
            if status != "available":
                continue
            eligible.append(product.product_id)
            ranking.append(
                self._ranked_item(
                    product, score, len(eligible), prior_product_id=prior_product_id)
            )
            if len(eligible) >= self.limit:
                break

        message_id = str(self.new_id())
        published_at = self.now().astimezone(timezone.utc)
        self.store.enqueue_ready(
            session_id=session_id,
            expected_context_version=observed_context_version,
            message_id=message_id,
            correlation_id=correlation_id.strip(),
            subject_reference=subject_reference.strip(),
            published_at=published_at,
            eligible_product_ids=eligible,
            ranking=ranking,
        )
        return RecommendationReady(
            message_id, observed_context_version, eligible, ranking
        )

    def preview(self, *, intent: dict, session_id: str | None = None) -> list[dict]:
        """Read-only availability-aware ranking for the workspace recommendations facet.

        Ranks the catalog against current intent and annotates each candidate with a
        real-time Available badge from a non-authoritative availability read
        (FR-011). Publishes nothing and writes no state: recommendations are a
        derived projection that regenerates from intent, so the stream's
        `recommendations` invalidation prompts the browser to refetch. Authoritative
        availability validation happens at selection time.
        """
        facets = self._intent(intent)
        if not facets:
            return []
        prior_product_id = self._prior_product_id(session_id)
        scored = self._rank(facets, prior_product_id=prior_product_id)
        product_ids = [product.product_id for product, _score in scored]
        availability = (self.inventory.availability(product_ids=product_ids)
                        if product_ids else {})
        items: list[dict] = []
        for product, score in scored:
            status = availability.get(product.product_id, {}).get("status", "unknown")
            items.append(self._ranked_item(
                product, score, len(items) + 1,
                available=status == "available",
                availability_status=status,
                prior_product_id=prior_product_id,
            ))
            if len(items) >= self.limit:
                break
        return items

    def _prior_product_id(self, session_id: str | None) -> str | None:
        if not isinstance(session_id, str) or not session_id.strip():
            return None
        if self.prior_product_lookup is None:
            return None
        try:
            value = self.prior_product_lookup(session_id.strip())
        except Exception:
            return None
        if not isinstance(value, str) or not value.strip():
            return None
        return value.strip()

    def _rank(
        self, facets: dict, *, prior_product_id: str | None = None,
    ) -> list[tuple[CatalogProduct, float]]:
        scored: list[tuple[CatalogProduct, float]] = []
        budget = facets.get("budget")
        occasion = facets.get("occasion")
        style = facets.get("style")
        flower = facets.get("flower_preference")
        for product in self.catalog:
            if budget is not None and product.price > budget:
                continue
            score = 0.0
            if occasion and occasion in product.occasions:
                score += 3.0
            if flower and flower in product.flowers:
                score += 2.0
            if style and style in product.styles:
                score += 1.0
            if budget is not None:
                # Prefer closer-to-budget options without exceeding it.
                score += max(0.0, 1.0 - (product.price / budget))
            if prior_product_id and product.product_id == prior_product_id:
                score += PRIOR_ORDER_HINT_SCORE
            scored.append((product, round(score, 4)))
        scored.sort(key=lambda item: (
            -item[1],
            0 if prior_product_id and item[0].product_id == prior_product_id else 1,
            item[0].product_id,
        ))
        return scored

    @staticmethod
    def _ranked_item(
        product: CatalogProduct,
        score: float,
        rank: int,
        *,
        available: bool | None = None,
        availability_status: str | None = None,
        prior_product_id: str | None = None,
    ) -> dict:
        item = {
            "product_id": product.product_id,
            "score": score,
            "rank": rank,
            "price": product.price,
        }
        if available is not None:
            item["available"] = available
            item["availability_status"] = availability_status
        if prior_product_id and product.product_id == prior_product_id:
            item["prior_order_hint"] = True
        return item

    @staticmethod
    def _intent(value: dict) -> dict:
        if not isinstance(value, dict):
            raise RecommendationValidationError("intent must be an object")
        allowed = {
            "occasion",
            "budget",
            "recipient",
            "style",
            "flower_preference",
            "timing",
        }
        unknown = set(value) - allowed
        if unknown:
            raise RecommendationValidationError(
                f"unsupported intent facets: {sorted(unknown)}"
            )
        facets: dict = {}
        for key, raw in value.items():
            if key == "budget":
                if isinstance(raw, bool) or not isinstance(raw, (int, float)) or raw <= 0:
                    raise RecommendationValidationError("budget is invalid")
                facets[key] = float(raw)
                continue
            if not isinstance(raw, str) or not raw.strip():
                raise RecommendationValidationError(f"{key} is invalid")
            facets[key] = raw.strip().lower()
        return facets
