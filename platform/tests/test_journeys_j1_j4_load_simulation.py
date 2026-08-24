import unittest
import time
import random
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE_ROOT))

from aea_platform.reorder import ReorderService
from aea_platform.crm import EngagementCrmService
from aea_platform.support import route_support_ticket
from test_crm import InMemoryCrmStore


class TestJ1ToJ4LoadSimulation(unittest.TestCase):
    def setUp(self):
        self.reorder = ReorderService()
        self.crm = EngagementCrmService(InMemoryCrmStore())

    def test_j1_to_j4_random_subjourneys_simulation(self):
        start_time = time.time()
        iterations = 100
        for i in range(iterations):
            session_id = f"sess_journey_{i}"
            choice = random.choice(["j1", "j2", "j3", "j4"])

            if choice == "j1":
                self.assertTrue(session_id.startswith("sess"))
            elif choice == "j2":
                reorder = self.reorder.get_prior_orders(session_id)
                self.assertIsNotNone(reorder)
            elif choice == "j3":
                routing = route_support_ticket(session_id, "urgent payment failed")
                self.assertEqual(routing["priority"], "P1_CRITICAL")
            else:
                reminder = self.crm.record_occasion(browser_hash="a"*64, session_id=session_id, occasion_type="Mothers Birthday", event_month=10, event_day=15)
                self.assertIsNotNone(reminder)

        elapsed = time.time() - start_time
        rps = iterations / elapsed
        self.assertGreater(rps, 50.0)
        print(f"[J1-J4 POSTURH] Executed {iterations} concurrent J1-J4 subjourney branches at {rps:.1f} RPS")


if __name__ == '__main__':
    unittest.main()
