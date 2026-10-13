"""Run offline: python -m unittest discover -s scripts -v"""
import tempfile
import unittest
from pathlib import Path

from broker_state import StateStore


ORDER = {"exchange": "NSE", "tradingsymbol": "EXAMPLE", "transaction_type": "BUY",
         "product": "CNC", "order_type": "LIMIT", "quantity": 100, "price": 10}


def event(status, filled, at, order_id="SIM1"):
    return {"order_id": order_id, "status": status, "quantity": 100,
            "filled": filled, "observed_at": at}


class BrokerStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "state.sqlite"
        self.store = StateStore(self.path)
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(lambda: self.store.close())

    def submitted(self, intent="signal1", ack=True):
        self.store.create_intent(intent, ORDER)
        command = self.store.begin_submission(intent)
        if ack:
            self.store.acknowledge(intent, "SIM1")
        return command

    def test_duplicate_updates_do_not_double_fill(self):
        self.submitted()
        update = event("UPDATE", 40, 1)
        self.assertTrue(self.store.apply_event(update))
        self.assertFalse(self.store.apply_event(update))
        self.assertEqual(self.store.order("SIM1")["filled"], 40)
        self.assertEqual(self.store.order("SIM1")["state"], "partially_filled")

    def test_late_open_does_not_erase_completion(self):
        self.submitted()
        self.store.apply_event(event("COMPLETE", 100, 3))
        self.store.apply_event(event("OPEN", 0, 1))
        state = self.store.order("SIM1")
        self.assertEqual((state["status"], state["filled"], state["remaining"]), ("COMPLETE", 100, 0))

    def test_timeout_reconciliation_recovers_original_without_retry(self):
        command = self.submitted(ack=False)
        self.store.submission_unknown("signal1")
        with self.assertRaises(RuntimeError):
            self.store.begin_submission("signal1")
        snapshot = dict(event("OPEN", 0, 1), tag=command["tag"], order=ORDER)
        self.assertEqual(self.store.reconcile_submission("signal1", [snapshot]), "matched")
        self.assertEqual(self.store.intent("signal1")["order_id"], "SIM1")
        with self.assertRaises(RuntimeError):
            self.store.begin_submission("signal1")

    def test_missing_or_multiple_matches_do_not_authorize_resend(self):
        command = self.submitted(ack=False)
        self.store.submission_unknown("signal1")
        self.assertEqual(self.store.reconcile_submission("signal1", []), "unresolved")
        one = dict(event("OPEN", 0, 1), tag=command["tag"], order=ORDER)
        two = dict(one, order_id="SIM2")
        self.assertEqual(self.store.reconcile_submission("signal1", [one, two]), "unresolved")
        self.assertIn("signal1", self.store.blocked_intents())
        with self.assertRaises(RuntimeError):
            self.store.begin_submission("signal1")

    def test_partial_fill_cancel_race_keeps_fills_and_residual(self):
        self.submitted()
        self.store.apply_event(event("UPDATE", 40, 1))
        self.store.request_cancel("SIM1")
        with self.assertRaises(RuntimeError):
            self.store.replacement_quantity("SIM1")
        self.store.apply_event(event("UPDATE", 60, 2))
        self.store.apply_event(event("CANCELLED", 60, 3))
        self.assertEqual(self.store.replacement_quantity("SIM1"), 40)
        self.assertEqual(self.store.order("SIM1")["filled"], 60)

    def test_restart_preserves_pending_intent_and_blocks_resend(self):
        self.submitted(ack=False)
        self.store.close()
        self.store = StateStore(self.path)
        self.assertEqual(self.store.intent("signal1")["state"], "SUBMITTING")
        self.assertIn("signal1", self.store.blocked_intents())
        with self.assertRaises(RuntimeError):
            self.store.begin_submission("signal1")

    def test_restart_known_open_order_requires_reconciliation(self):
        self.submitted()
        self.store.close()
        self.store = StateStore(self.path)
        self.assertIn("signal1", self.store.blocked_intents())

    def test_changed_payload_cannot_reuse_intent(self):
        self.store.create_intent("signal1", ORDER)
        with self.assertRaises(ValueError):
            self.store.create_intent("signal1", dict(ORDER, quantity=200))

    def test_conflicting_fill_regression_blocks_replacement(self):
        self.submitted()
        self.store.apply_event(event("UPDATE", 60, 1))
        self.store.apply_event(event("CANCELLED", 40, 2))
        self.assertEqual(self.store.order("SIM1")["filled"], 60)
        self.assertIn("signal1", self.store.blocked_intents())
        with self.assertRaises(RuntimeError):
            self.store.replacement_quantity("SIM1")

    def test_late_fill_after_cancel_preserves_fill_and_requires_recheck(self):
        self.submitted()
        self.store.apply_event(event("CANCELLED", 40, 2))
        self.store.apply_event(event("UPDATE", 60, 3))
        state = self.store.order("SIM1")
        self.assertEqual((state["status"], state["filled"]), ("CANCELLED", 60))
        with self.assertRaises(RuntimeError):
            self.store.replacement_quantity("SIM1")

    def test_acknowledging_known_order_cannot_clear_a_conflict(self):
        self.submitted()
        self.store.apply_event(event("UPDATE", 60, 1))
        self.store.apply_event(event("CANCELLED", 40, 2))
        self.store.acknowledge("signal1", "SIM1")
        self.assertIn("signal1", self.store.blocked_intents())


if __name__ == "__main__":
    unittest.main()
