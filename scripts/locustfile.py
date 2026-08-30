import uuid
import random
from locust import HttpUser, task, between, SequentialTaskSet


class J1StandardShopperJourney(SequentialTaskSet):
    @task
    def land_on_workspace(self):
        self.client.get(f"/api/v1/sessions/{self.user.session_id}", name="J1: Land on Tile T-01")

    @task
    def place_order(self):
        payload = {"session_id": self.user.session_id, "sku": "SKU-MOM-BDAY-01", "quantity": 1}
        self.client.post("/api/v1/orders", json=payload, name="J1: Place Order")


class J2ReorderShopperJourney(SequentialTaskSet):
    @task
    def recall_prior_orders(self):
        self.client.get(f"/api/v1/reorder/{self.user.session_id}", name="J2: Recall Prior Orders")

    @task
    def fast_reorder(self):
        payload = {"session_id": self.user.session_id, "prior_order_id": "ORD-9988"}
        self.client.post("/api/v1/reorder/prepare", json=payload, name="J2: Fast Reorder")


class J3SupportLiveChatJourney(SequentialTaskSet):
    @task
    def ask_delivery_faq(self):
        self.client.get("/api/v1/support/faq?q=delivery_policy", name="J3: Ask Delivery FAQ")

    @task
    def open_live_chat(self):
        payload = {"session_id": self.user.session_id, "customer_name": "Shopper"}
        self.client.post("/api/v1/livechat/tickets", json=payload, name="J3: Open Live Chat")

    @task
    def route_priority_support(self):
        payload = {"session_id": self.user.session_id, "reason": "urgent payment failed"}
        self.client.post("/api/v1/support/route", json=payload, name="J3: Priority Support Route")


class J4OccasionCRMJourney(SequentialTaskSet):
    @task
    def register_occasion(self):
        payload = {"session_id": self.user.session_id, "occasion": "Anniversary", "date": "2026-10-15"}
        self.client.post("/api/v1/crm/reminders", json=payload, name="J4: Register Occasion")


class AEAConcurrentJourneyUser(HttpUser):
    wait_time = between(0.1, 0.5)
    tasks = {
        J1StandardShopperJourney: 40,
        J2ReorderShopperJourney: 25,
        J3SupportLiveChatJourney: 20,
        J4OccasionCRMJourney: 15
    }

    def on_start(self):
        self.session_id = f"sess_i_{uuid.uuid4().hex[:8]}"

    @task(10)
    def random_subjourney_branching(self):
        choice = random.choice(["v1", "v2", "v3", "v4"])
        self.client.get(f"/api/v1/sessions/{self.session_id}", name="Subjourney: Random Branch")
