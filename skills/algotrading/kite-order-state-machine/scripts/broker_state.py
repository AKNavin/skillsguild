"""Offline, standard-library reference for durable Kite-style order state.

No network client or live execution is present. A real adapter must independently
validate broker identity, current scope, order fields and account ownership.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path


TERMINAL = {"COMPLETE", "CANCELLED", "REJECTED"}
OPEN_INTENTS = {"SUBMITTING", "SUBMIT_UNKNOWN", "ACCEPTED"}


def canonical(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def fingerprint(value: dict) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class StateStore:
    def __init__(self, path: str | Path):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS intents (
                intent_id TEXT PRIMARY KEY,
                fingerprint TEXT NOT NULL,
                payload TEXT NOT NULL,
                tag TEXT NOT NULL UNIQUE,
                state TEXT NOT NULL,
                order_id TEXT UNIQUE,
                reconcile_required INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                intent_id TEXT UNIQUE REFERENCES intents(intent_id),
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                filled INTEGER NOT NULL DEFAULT 0 CHECK(filled >= 0),
                status TEXT NOT NULL,
                observed_at INTEGER NOT NULL DEFAULT -1,
                reconcile_required INTEGER NOT NULL DEFAULT 0,
                cancel_requested INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS events (
                event_key TEXT PRIMARY KEY,
                order_id TEXT NOT NULL REFERENCES orders(order_id),
                payload TEXT NOT NULL
            );
        """)
        # Existing open state must be reconciled after every process restart.
        self.db.execute("""UPDATE intents SET reconcile_required=1
                           WHERE state IN ('SUBMITTING','SUBMIT_UNKNOWN','ACCEPTED')""")

    def close(self):
        self.db.close()

    @contextmanager
    def transaction(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def intent(self, intent_id: str) -> dict:
        row = self.db.execute("SELECT * FROM intents WHERE intent_id=?", (intent_id,)).fetchone()
        if row is None:
            raise KeyError(intent_id)
        return dict(row)

    def order(self, order_id: str) -> dict:
        row = self.db.execute("SELECT * FROM orders WHERE order_id=?", (order_id,)).fetchone()
        if row is None:
            raise KeyError(order_id)
        result = dict(row)
        result["remaining"] = max(0, result["quantity"] - result["filled"])
        result["state"] = (
            "partially_filled"
            if result["status"] not in TERMINAL and result["filled"] > 0
            else result["status"].lower()
        )
        return result

    def create_intent(self, intent_id: str, payload: dict) -> dict:
        quantity = payload.get("quantity")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("quantity must be a positive integer")
        for field in ("exchange", "tradingsymbol", "transaction_type", "product"):
            if not payload.get(field):
                raise ValueError(f"missing {field}")
        digest = fingerprint(payload)
        tag = hashlib.sha256(intent_id.encode()).hexdigest()[:20]
        with self.transaction():
            old = self.db.execute("SELECT fingerprint FROM intents WHERE intent_id=?", (intent_id,)).fetchone()
            if old and old["fingerprint"] != digest:
                raise ValueError("intent ID reused with different order parameters")
            self.db.execute("""INSERT OR IGNORE INTO intents
                (intent_id,fingerprint,payload,tag,state) VALUES(?,?,?,?, 'NEW')""",
                (intent_id, digest, canonical(payload), tag))
        return self.intent(intent_id)

    def begin_submission(self, intent_id: str) -> dict:
        """Return an offline command once; the caller may simulate transport."""
        with self.transaction():
            item = self.intent(intent_id)
            if item["state"] != "NEW" or item["reconcile_required"]:
                raise RuntimeError("intent is not eligible for submission; reconcile it")
            self.db.execute("UPDATE intents SET state='SUBMITTING' WHERE intent_id=?", (intent_id,))
        return {"intent_id": intent_id, "tag": item["tag"], "order": json.loads(item["payload"])}

    def submission_unknown(self, intent_id: str):
        with self.transaction():
            item = self.intent(intent_id)
            if item["state"] in {"SUBMITTING", "SUBMIT_UNKNOWN"}:
                self.db.execute("""UPDATE intents SET state='SUBMIT_UNKNOWN',
                    reconcile_required=1 WHERE intent_id=?""", (intent_id,))

    def acknowledge(self, intent_id: str, order_id: str):
        with self.transaction():
            self._acknowledge(intent_id, order_id)

    def _acknowledge(self, intent_id: str, order_id: str):
        item = self.intent(intent_id)
        if item["state"] == "NEW":
            raise RuntimeError("intent was never submitted")
        if item["order_id"] and item["order_id"] != order_id:
            raise ValueError("intent already belongs to another order")
        payload = json.loads(item["payload"])
        self.db.execute("""INSERT OR IGNORE INTO orders
            (order_id,intent_id,quantity,status) VALUES(?,?,?,'PENDING')""",
            (order_id, intent_id, payload["quantity"]))
        existing = self.order(order_id)
        if existing["intent_id"] != intent_id:
            raise ValueError("broker order already belongs to another intent")
        state = existing["status"] if existing["status"] in TERMINAL else "ACCEPTED"
        self.db.execute("""UPDATE intents SET order_id=?,state=?,reconcile_required=?
                           WHERE intent_id=?""",
                        (order_id, state, existing["reconcile_required"], intent_id))

    def apply_event(self, event: dict) -> bool:
        """Reduce normalized fixture events; observed_at is an integer event time.

        Real integrations should obtain fills from unique broker trades, too.
        This compact reducer uses monotone cumulative fills and flags conflicts.
        """
        required = {"order_id", "status", "quantity", "filled", "observed_at"}
        if not required.issubset(event):
            raise ValueError("incomplete normalized order event")
        if event["status"] not in {"PENDING", "OPEN", "TRIGGER_PENDING", "UPDATE"} | TERMINAL:
            raise ValueError("unsupported normalized status")
        for field in ("quantity", "filled", "observed_at"):
            if isinstance(event[field], bool) or not isinstance(event[field], int):
                raise ValueError(f"{field} must be an integer")
        if event["quantity"] <= 0 or not 0 <= event["filled"] <= event["quantity"]:
            raise ValueError("impossible quantities")
        key = fingerprint(event)
        with self.transaction():
            old = self.order(event["order_id"])
            if self.db.execute("SELECT 1 FROM events WHERE event_key=?", (key,)).fetchone():
                return False
            self.db.execute("INSERT INTO events VALUES(?,?,?)", (key, event["order_id"], canonical(event)))
            newer = event["observed_at"] >= old["observed_at"]
            conflict = bool(old["reconcile_required"])
            if event["quantity"] != old["quantity"]:
                # Quantity modifications require a separate validated adapter.
                conflict = True
            filled = max(old["filled"], event["filled"])
            if newer and event["filled"] < old["filled"]:
                conflict = True
            status = old["status"]
            incoming = event["status"]
            if old["status"] in TERMINAL:
                if incoming in TERMINAL and incoming != old["status"]:
                    conflict = True
                if filled > old["filled"]:
                    conflict = True
                # Preserve a terminal state while retaining any late fill evidence.
            elif newer:
                status = incoming if incoming != "UPDATE" else (old["status"] if old["status"] != "PENDING" else "OPEN")
            elif incoming in TERMINAL:
                conflict = True
            if status == "COMPLETE" and filled != old["quantity"]:
                conflict = True
            self.db.execute("""UPDATE orders SET filled=?,status=?,observed_at=?,
                reconcile_required=? WHERE order_id=?""",
                (filled, status, max(old["observed_at"], event["observed_at"]), int(conflict), event["order_id"]))
            if old["intent_id"]:
                self.db.execute("""UPDATE intents SET state=?,reconcile_required=?
                                   WHERE intent_id=?""",
                    (status if status in TERMINAL else "ACCEPTED", int(conflict), old["intent_id"]))
        return True

    def request_cancel(self, order_id: str) -> dict:
        """Record a proposed cancel; do not assume a cancel acknowledgement is final."""
        item = self.order(order_id)
        if item["status"] in TERMINAL:
            return {"order_id": order_id, "action": "none"}
        self.db.execute("UPDATE orders SET cancel_requested=1 WHERE order_id=?", (order_id,))
        return {"order_id": order_id, "action": "cancel_requested"}

    def replacement_quantity(self, order_id: str) -> int:
        item = self.order(order_id)
        if item["status"] != "CANCELLED" or item["reconcile_required"]:
            raise RuntimeError("confirm cancellation and reconcile fills before replacement")
        return item["remaining"]

    def reconcile_submission(self, intent_id: str, snapshots: list[dict]) -> str:
        """Match simulated broker snapshots. Empty/ambiguous evidence never resends."""
        item = self.intent(intent_id)
        matches = [s for s in snapshots if s.get("tag") == item["tag"]
                   and fingerprint(s.get("order", {})) == item["fingerprint"]]
        if len(matches) != 1:
            self.submission_unknown(intent_id)
            self.db.execute("UPDATE intents SET reconcile_required=1 WHERE intent_id=?", (intent_id,))
            return "unresolved"
        match = matches[0]
        self.acknowledge(intent_id, match["order_id"])
        self.apply_event({k: match[k] for k in ("order_id", "status", "quantity", "filled", "observed_at")})
        return "matched" if not self.intent(intent_id)["reconcile_required"] else "conflict"

    def blocked_intents(self) -> list[str]:
        return [r[0] for r in self.db.execute("""SELECT intent_id FROM intents
            WHERE reconcile_required=1 OR state IN ('SUBMITTING','SUBMIT_UNKNOWN')
            ORDER BY intent_id""")]
