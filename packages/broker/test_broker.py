"""Offline tests: fake credentials and mocked broker transport only."""
import csv
import datetime as dt
import hashlib
import http.client
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.parse

from broker_core import BrokerError, BrokerSession, IST, Limiter, authenticate, normalize_candles, transport, validate_range
from broker_login import LocalServer, MAX_BODY
from download import LocalClient, download_dataset, read_instruments


class FakeClock:
    def __init__(self):
        self.now = 0
        self.sleeps = []
    def clock(self):
        return self.now
    def sleep(self, delay):
        self.sleeps.append(delay)
        self.now += delay


def fake_session(broker="zerodha", responses=None, plan="standard"):
    recorded = []
    responses = iter(responses or [(200, {"data": {}}, None)])
    def request(method, url, headers, data):
        recorded.append((method, url, headers, data))
        return next(responses)
    clock = FakeClock()
    limiter = Limiter(broker, plan, clock.clock, clock.sleep)
    return BrokerSession(broker, "fake-app", "fake-token", plan, request, limiter), recorded, clock


class AdapterTests(unittest.TestCase):
    def test_zerodha_code_checksum_and_secret_not_retained(self):
        calls = []
        def request(method, url, headers, data):
            calls.append((method, url, headers, data))
            return (200, {"status": "success", "data": {"access_token": "fake-token"}} if method == "POST" else {"status": "success", "data": {}}, None)
        fields = {"broker": "zerodha", "mode": "code", "client_id": "fake-key", "secret": "fake-secret", "code": "fake-code"}
        session = authenticate(fields, request)
        sent = urllib.parse.parse_qs(calls[0][3].decode())
        self.assertEqual(sent["checksum"], [hashlib.sha256(b"fake-keyfake-codefake-secret").hexdigest()])
        self.assertNotIn(b"fake-secret", calls[0][3])
        self.assertNotIn("fake-secret", repr(session.__dict__))
        session.clear()
        self.assertEqual(session.token, "")

    def test_fyers_code_exchange(self):
        calls = []
        def request(method, url, headers, data):
            calls.append((method, url, data))
            return (200, {"s": "ok", "access_token": "fake-token"}, None)
        authenticate({"broker": "fyers", "mode": "code", "client_id": "APP-100", "secret": "fake-secret", "code": "fake-code"}, request)
        self.assertEqual(json.loads(calls[0][2])["appIdHash"], hashlib.sha256(b"APP-100:fake-secret").hexdigest())

    def test_dhan_checks_client_identity(self):
        with self.assertRaisesRegex(BrokerError, "does not match"):
            authenticate({"broker": "dhan", "client_id": "123", "access_token": "fake-token"}, lambda *args: (200, {"dhanClientId": "456"}, None))

    def test_auth_errors_redact_payload(self):
        with self.assertRaises(BrokerError) as caught:
            authenticate({"broker": "zerodha", "client_id": "fake-app", "access_token": "fake-token"}, lambda *args: (403, {"message": "secret-from-broker fake-token"}, None))
        self.assertNotIn("fake-token", str(caught.exception))
        self.assertNotIn("secret-from-broker", str(caught.exception))

    def test_transport_endpoint_allowlist(self):
        for url in ("http://api.kite.trade/user/profile", "https://example.com/", "http://127.0.0.1/"):
            with self.assertRaises(BrokerError):
                transport("GET", url)

    def test_invalid_credentials_do_not_reach_transport(self):
        with self.assertRaises(BrokerError):
            authenticate({"broker": "zerodha", "client_id": "x\r\nheader", "access_token": "fake-token"}, lambda *args: self.fail("network attempted"))

    def test_retry_429_and_503_then_success(self):
        session, calls, clock = fake_session(responses=[(429, {}, "2"), (503, {}, None), (200, {"data": {}}, None)])
        session.call("GET", "https://api.kite.trade/user/profile")
        self.assertEqual(len(calls), 3)
        self.assertGreaterEqual(clock.now, 6)

    def test_auth_failure_stops_without_retry_and_clears(self):
        session, calls, _ = fake_session(responses=[(403, {"message": "fake-token"}, None)])
        with self.assertRaises(BrokerError):
            session.call("GET", "https://api.kite.trade/user/profile")
        self.assertEqual(len(calls), 1)
        self.assertEqual(session.token, "")
        self.assertFalse(session.active)

    def test_bad_input_stops_without_retry(self):
        session, calls, _ = fake_session(responses=[(400, {}, None)])
        with self.assertRaises(BrokerError):
            session.call("GET", "https://api.kite.trade/user/profile")
        self.assertEqual(len(calls), 1)

    def test_long_cooldown_stops(self):
        session, calls, _ = fake_session(responses=[(429, {}, "86400")])
        with self.assertRaisesRegex(BrokerError, "cooldown"):
            session.call("GET", "https://api.kite.trade/user/profile")
        self.assertEqual(len(calls), 1)

    def test_retries_bounded(self):
        session, calls, _ = fake_session(responses=[(503, {}, None)] * 4)
        with self.assertRaisesRegex(BrokerError, "four attempts"):
            session.call("GET", "https://api.kite.trade/user/profile")
        self.assertEqual(len(calls), 4)

    def test_standard_fyers_minute_and_daily_limits(self):
        clock = FakeClock()
        limiter = Limiter("fyers", clock=clock.clock, sleep=clock.sleep)
        for _ in range(49):
            limiter.wait()
        self.assertGreaterEqual(clock.now, 60)
        limiter.per_day = 49
        with self.assertRaisesRegex(BrokerError, "daily"):
            limiter.wait()

    def test_dhan_noninclusive_to_date_and_array_conversion(self):
        stamp = int(dt.datetime(2020, 1, 2, tzinfo=IST).timestamp())
        session, calls, _ = fake_session("dhan", [(200, {"timestamp": [stamp], "open": [100], "high": [105], "low": [99], "close": [102], "volume": [1000]}, None)])
        rows = session.history({"dhan_security_id": "123", "kind": "stock"}, "2020-01-01", "2020-01-03")
        self.assertEqual(json.loads(calls[0][3])["toDate"], "2020-01-04")
        self.assertEqual(rows[0]["date"], "2020-01-02")

    def test_fyers_application_errors_use_retry(self):
        session, calls, _ = fake_session("fyers", [(200, {"s": "error", "code": -429}, None), (200, {"s": "ok"}, None)])
        session.call("GET", "https://api-t1.fyers.in/api/v3/profile")
        self.assertEqual(len(calls), 2)

    def test_future_and_current_candles_rejected(self):
        with self.assertRaises(BrokerError):
            validate_range("2020-01-01", "2020-01-02", today=dt.date(2020, 1, 2))

    def test_ohlc_and_duplicate_validation(self):
        start, end = dt.date(2020, 1, 1), dt.date(2020, 1, 3)
        with self.assertRaises(BrokerError):
            normalize_candles([["2020-01-02", 100, 99, 98, 101, 1]], start, end)
        with self.assertRaises(BrokerError):
            normalize_candles([["2020-01-02", 100, 102, 98, 101, 1], ["2020-01-02", 100, 102, 98, 102, 1]], start, end)

    def test_no_derivative_history(self):
        session, calls, _ = fake_session()
        with self.assertRaises(BrokerError):
            session.history({"kind": "future", "zerodha_token": "123"}, "2020-01-01", "2020-01-02")
        self.assertEqual(calls, [])


class LocalBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.messages, self.received = [], []
        def auth(fields):
            self.received.append(dict(fields))
            return BrokerSession("zerodha", "fake-key", "fake-token")
        self.server = LocalServer(authenticator=auth, notify=self.messages.append)
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        conn.request(method, path, body, headers or {})
        result = conn.getresponse()
        status, response_headers, raw = result.status, dict(result.getheaders()), result.read()
        conn.close()
        return status, response_headers, raw

    def login(self, **overrides):
        data = {"broker": "zerodha", "mode": "token", "client_id": "fake-key", "access_token": "fake-token", "csrf": self.server.csrf}
        headers = {"Origin": self.server.origin, "Cookie": "sg_local=" + self.server.cookie, "Content-Type": "application/x-www-form-urlencoded"}
        headers.update(overrides)
        return self.request("POST", "/authenticate", urllib.parse.urlencode(data), headers)

    def test_login_page_security_headers_no_resources(self):
        status, headers, raw = self.request("GET", "/login/" + self.server.login_key)
        self.assertEqual(status, 200)
        self.assertIn("no-store", headers["Cache-Control"])
        self.assertIn("default-src 'none'", headers["Content-Security-Policy"])
        self.assertIn("HttpOnly", headers["Set-Cookie"])
        self.assertNotIn(b"<script", raw)
        self.assertNotIn("Access-Control-Allow-Origin", headers)

    def test_dns_rebinding_host_rejected(self):
        self.assertEqual(self.request("GET", "/login/" + self.server.login_key, headers={"Host": "attacker.example"})[0], 403)

    def test_cross_origin_rejected(self):
        self.assertEqual(self.login(Origin="https://attacker.example")[0], 403)
        self.assertFalse(self.received)

    def test_missing_cookie_rejected(self):
        self.assertEqual(self.login(Cookie="")[0], 400)
        self.assertFalse(self.received)

    def test_missing_csrf_rejected(self):
        body = urllib.parse.urlencode({"broker": "zerodha", "client_id": "fake-key", "access_token": "fake-token"})
        status = self.request("POST", "/authenticate", body, {"Origin": self.server.origin, "Cookie": "sg_local=" + self.server.cookie, "Content-Type": "application/x-www-form-urlencoded"})[0]
        self.assertEqual(status, 400)
        self.assertFalse(self.received)

    def test_body_size_enforced(self):
        status = self.request("POST", "/authenticate", "x" * (MAX_BODY + 1), {"Origin": self.server.origin, "Cookie": "sg_local=" + self.server.cookie, "Content-Type": "application/x-www-form-urlencoded"})[0]
        self.assertEqual(status, 400)
        self.assertFalse(self.received)

    def test_connected_output_is_not_a_credential(self):
        status, _, raw = self.login()
        self.assertEqual(status, 200)
        self.assertNotIn(b"fake-token", raw)
        self.assertNotIn("fake-token", "".join(self.messages))
        key = self.server.session_key
        status, _, raw = self.request("GET", "/session/" + key + "/status", headers={"X-SkillsGuild-Request": "history-client"})
        self.assertEqual(status, 200)
        self.assertNotIn(b"fake-token", raw)
        self.assertEqual(json.loads(raw)["permissions"], ["daily-history"])

    def test_capability_requires_custom_header(self):
        self.login()
        self.assertEqual(self.request("GET", "/session/" + self.server.session_key + "/status")[0], 403)

    def test_arbitrary_endpoints_not_exposed(self):
        self.login()
        self.assertEqual(self.request("POST", "/session/" + self.server.session_key + "/orders", "{}")[0], 404)


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.mapping = self.root / "instruments.csv"
        self.mapping.write_text("symbol,kind,industry,zerodha_token\nNIFTY_500,index,,1\nNIFTY_50,index,,2\nTEST,stock,Technology,3\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_benchmarks_required(self):
        self.mapping.write_text("symbol,kind,industry,zerodha_token\nTEST,stock,Technology,3\n", encoding="utf-8")
        with self.assertRaisesRegex(BrokerError, "Map both"):
            read_instruments(self.mapping, "zerodha")

    def test_credentials_column_rejected(self):
        self.mapping.write_text("symbol,kind,industry,access_token\nTEST,stock,Technology,fake-token\n", encoding="utf-8")
        with self.assertRaisesRegex(BrokerError, "Credentials"):
            read_instruments(self.mapping, "zerodha")

    def test_session_url_restricted_to_loopback(self):
        for url in ("https://example.com/session/" + "x" * 43, "http://localhost:1234/session/" + "x" * 43, "http://127.0.0.1:1234/orders"):
            with self.assertRaises(BrokerError):
                LocalClient(url)

    def test_resume_and_manifest_hashes_and_quarantine(self):
        class Client:
            calls = 0
            def call(inner, route, body=None):
                if route == "/status":
                    return {"broker": "zerodha", "connected": True, "plan": "standard"}
                inner.calls += 1
                dates = ["2020-01-01", "2020-01-02", "2020-01-03"]
                if body["instrument"]["symbol"] == "TEST":
                    dates.remove("2020-01-02")
                return {"candles": [{"date": date, "open": 100, "high": 102, "low": 99, "close": 101, "volume": 1000} for date in dates]}
        client = Client()
        output = self.root / "dataset"
        first = download_dataset(client, self.mapping, "2020-01-01", "2020-01-03", output, progress=lambda *args: None)
        self.assertEqual(client.calls, 3)
        self.assertEqual(first["quarantined_symbols"], [])
        self.assertEqual(first["coverage"]["TEST"]["internal_dates_missing_vs_nifty500"], ["2020-01-02"])
        self.assertEqual(first["retained_shared_sessions"], 0)
        second = download_dataset(client, self.mapping, "2020-01-01", "2020-01-03", output, progress=lambda *args: None)
        self.assertEqual(client.calls, 3)
        for name, sha in second["files"].items():
            self.assertEqual(sha, hashlib.sha256((output / name).read_bytes()).hexdigest())
        with self.assertRaisesRegex(BrokerError, "different broker"):
            download_dataset(client, self.mapping, "2020-01-01", "2020-01-04", output, progress=lambda *args: None)

    def test_100_stock_download_runs_research_after_index_only_session(self):
        research = Path(__file__).resolve().parents[1] / "research"
        self.assertTrue((research / "runner.py").is_file(), "Run this integration test from the complete strategy package")
        dates = []
        day = dt.date(2019, 1, 1)
        while len(dates) < 360:
            if day.weekday() < 5:
                dates.append(day.isoformat())
            day += dt.timedelta(days=1)
        special = "2019-01-05"
        self.mapping.write_text("symbol,kind,industry,zerodha_token\nNIFTY_500,index,,1\nNIFTY_50,index,,2\n" + "".join(f"S{i:03},stock,Industry{i % 10},{i + 10}\n" for i in range(100)), encoding="utf-8")
        class Client:
            def call(inner, route, body=None):
                if route == "/status":
                    return {"broker": "zerodha", "connected": True, "plan": "standard"}
                symbol = body["instrument"]["symbol"]
                available = sorted(dates + [special]) if symbol == "NIFTY_500" else dates
                offset = int(symbol[1:]) if symbol.startswith("S") else 0
                rows = []
                for i, date in enumerate(available):
                    if body["from"] <= date <= body["to"]:
                        price = 100 + offset + i * 0.12 + math.sin(i / 11) * 0.5
                        rows.append({"date": date, "open": price, "high": price * 1.01, "low": price * .99, "close": price * 1.001, "volume": 10_000_000})
                return {"candles": rows}
        output = self.root / "complete-panel"
        manifest = download_dataset(Client(), self.mapping, dates[0], dates[-1], output, progress=lambda *args: None)
        self.assertEqual(manifest["quarantined_symbols"], [])
        self.assertEqual(manifest["omitted_incomplete_sessions"], [{"date": special, "stock_bars": 0}])
        self.assertEqual(manifest["retained_shared_sessions"], len(dates))
        self.assertEqual(manifest["coverage"]["S000"]["internal_dates_missing_vs_nifty500"], [special])
        results = self.root / "research-output"
        completed = subprocess.run([sys.executable, "-B", str(research / "runner.py"), "--strategy", "high52", "--data-dir", str(output), "--start", dates[300], "--end", dates[-1], "--output", str(results)], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        audit = json.loads((results / "panel-audit.json").read_text())
        self.assertEqual(audit["stocks"], 100)
        self.assertEqual(audit["omitted_incomplete_sessions"], manifest["omitted_incomplete_sessions"])
        report = json.loads((results / "results.json").read_text())
        self.assertEqual(report["strategy_id"], "high52")
        self.assertLess(abs(report["accounting_residual"]), 1e-8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
