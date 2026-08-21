"""AEA System Readiness & Concurrency Load Testing Engine.

Validates system capacity, latency SLOs (NFR-004), and throughput across
randomized End-to-End Customer Journeys (J1-J4) for N concurrent users.
Coherent with NFR-003, NFR-004, NFR-011, ADR-001, ADR-005, ADR-010, and ADR-016.
"""

import json
import random
import uuid
from locust import HttpUser, TaskSet, between, task


OCCASIONS = ["Birthday", "Anniversary", "Get Well Soon", "Sympathy", "Just Because", "Congratulations"]
RECIPIENTS = ["Mother", "Partner", "Friend", "Colleague", "Grandmother"]
BUDGETS = [45, 65, 85, 120, 150, 200]
PRODUCT_IDS = ["bouquet-rose-classic", "bouquet-lily-sunburst", "arrangement-pastel-romance", "plant-orchid-elegant"]


class CustomerJourneyUser(HttpUser):
    """Simulates realistic customer journeys (J1-J4) with random variations."""

    wait_time = between(1.5, 5.0)  # Realistic user think-time between actions

    def on_start(self):
        """Initialize session headers and correlation tracking."""
        self.session_id = str(uuid.uuid4())
        self.headers = {
            "Content-Type": "application/json",
            "X-Session-ID": self.session_id,
            "X-Correlation-ID": str(uuid.uuid4()),
        }
        self.cart_items = []

    @task(35)
    def journey_j1_express_same_day(self):
        """J1: High-Urgency Same-Day Shopping (Weight: 35%).
        Fast intent -> Select recommendation -> Select slot -> Express checkout.
        """
        # 1. Express Intent Entry
        occasion = random.choice(OCCASIONS)
        budget = random.choice(BUDGETS)
        intent_payload = {
            "session_id": self.session_id,
            "raw_text": f"I need flowers for {occasion} today under ${budget}",
            "facets": {"occasion": occasion, "budget": budget, "delivery_speed": "same-day"},
        }
        with self.client.post("/api/v1/intent", json=intent_payload, headers=self.headers, catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"J1 Intent failed: {resp.status_code}")
                return

        # 2. Fetch Curated Recommendations (T-03)
        self.client.get(f"/api/v1/recommendations?session_id={self.session_id}", headers=self.headers)

        # 3. Product Selection & Cart Addition (T-04)
        product_id = random.choice(PRODUCT_IDS)
        selection_payload = {
            "session_id": self.session_id,
            "items": [{"product_id": product_id, "quantity": 1, "options": {"size": "Standard"}}],
        }
        self.client.post("/api/v1/selection", json=selection_payload, headers=self.headers)

        # 4. Delivery Slot Planning (T-05)
        delivery_payload = {
            "session_id": self.session_id,
            "slot_id": "today-afternoon-14-18",
            "recipient": {"name": "Test Recipient", "address": "123 Main St, Sydney"},
        }
        self.client.post("/api/v1/delivery", json=delivery_payload, headers=self.headers)

        # 5. Order Review & Payment Tokenization (T-06 / T-07)
        checkout_payload = {
            "session_id": self.session_id,
            "payment_token": f"tok_sandbox_{uuid.uuid4().hex[:8]}",
        }
        self.client.post("/api/v1/checkout", json=checkout_payload, headers=self.headers)

    @task(45)
    def journey_j2_planned_family_gift(self):
        """J2: Planned Family Gift & Customization (Weight: 45%).
        Refines intent multiple times -> Customizes size/ribbon -> Card message -> Checkout.
        """
        # 1. Initial Conversational Intent
        occasion = "Mother's Birthday"
        recipient = random.choice(RECIPIENTS)
        budget = random.choice(BUDGETS)
        self.client.post(
            "/api/v1/intent",
            json={"session_id": self.session_id, "raw_text": f"Flowers for my {recipient}'s {occasion}"},
            headers=self.headers,
        )

        # 2. Shared Understanding Chip Refinement (T-02 Intent Supersession ADR-005)
        self.client.post(
            "/api/v1/intent",
            json={"session_id": self.session_id, "facets": {"budget": budget, "pet_friendly": True}},
            headers=self.headers,
        )

        # 3. Custom Product Selection & Ribbon/Card Customization (T-04)
        selection_payload = {
            "session_id": self.session_id,
            "items": [
                {
                    "product_id": "arrangement-pastel-romance",
                    "quantity": 1,
                    "options": {
                        "size": "Deluxe",
                        "ribbon": "Satin Gold",
                        "card_message": "Happy Birthday Mom! Wishing you joy and love.",
                    },
                }
            ],
        }
        self.client.post("/api/v1/selection", json=selection_payload, headers=self.headers)

        # 4. Delivery Slot Selection (T-05)
        self.client.post(
            "/api/v1/delivery",
            json={"session_id": self.session_id, "slot_id": "tomorrow-morning-09-12"},
            headers=self.headers,
        )

    @task(15)
    def journey_j3_returning_shopper_recall(self):
        """J3: Accountless Instant Reorder & Recall (Weight: 15%).
        Same-browser recall -> Prior order hint -> Reorder.
        """
        # 1. Prior-Order Hint Lookup (FR-008 / M8)
        self.client.get(f"/api/v1/reorder/recall?session_id={self.session_id}", headers=self.headers)

        # 2. Execute Instant Reorder
        self.client.post(
            "/api/v1/reorder/execute",
            json={"session_id": self.session_id, "reorder_order_id": "ord_previous_12345"},
            headers=self.headers,
        )

    @task(5)
    def journey_j4_support_and_faq(self):
        """J4: Post-Purchase Status & ASO FAQ Overlay (Weight: 5%).
        Order tracking (T-08) -> ASO FAQ inquiry -> Contact Florist.
        """
        # 1. Order Tracking Inquiry (T-08)
        self.client.get(f"/api/v1/orders/status?session_id={self.session_id}", headers=self.headers)

        # 2. Automated Support Overlay Inquiry (ASO / FR-009)
        self.client.post(
            "/api/v1/support/faq",
            json={"session_id": self.session_id, "question": "What is your delivery cancellation policy?"},
            headers=self.headers,
        )

        # 3. Contact Florist Escalation Request (FR-006 / T-09)
        self.client.post(
            "/api/v1/escalations",
            json={"session_id": self.session_id, "reason": "Change delivery address"},
            headers=self.headers,
        )
