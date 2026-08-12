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


class RecommendationService:
    """Availability-aware recommendation ranking boundary (FR-007 / NFR-006)."""

    def __init__(
        self,
        store,
        inventory,
        *,
        catalog: Sequence[CatalogProduct] | None = None,
        limit: int = 10,
        now: Callable[[], datetime] | None = None,
        new_id: Callable[[], uuid.UUID] | None = None,
    ):
        if limit < 1 or limit > 50:
            raise ValueError("recommendation limit must be between 1 and 50")
        self.store = store
        self.inventory = inventory
        self.catalog = tuple(catalog) if catalog is not None else REFERENCE_CATALOG
        self.limit = limit
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.new_id = new_id or uuid.uuid4

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

        scored = self._rank(facets)
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
                {
                    "product_id": product.product_id,
                    "score": score,
                    "rank": len(eligible),
                    "price": product.price,
                }
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

    def _rank(self, facets: dict) -> list[tuple[CatalogProduct, float]]:
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
            scored.append((product, round(score, 4)))
        scored.sort(key=lambda item: (-item[1], item[0].product_id))
        return scored

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
