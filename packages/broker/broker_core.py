"""Read-only broker adapters. Python 3.10+, standard library only."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque

IST = dt.timezone(dt.timedelta(hours=5, minutes=30), "Asia/Kolkata")
MAX_RESPONSE = 16 * 1024 * 1024


class BrokerError(Exception):
    """Only fixed, non-secret text may be surfaced to the caller."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise BrokerError("Broker redirected the request; check the current API documentation.")


def transport(method, url, headers=None, data=None):
    """No proxies or redirects: credentials go only to fixed broker HTTPS hosts."""
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in {"api.kite.trade", "api.dhan.co", "api-t1.fyers.in"}:
        raise BrokerError("Unsupported broker endpoint.")
    headers = {"Accept": "application/json", "User-Agent": "SkillsGuild-Research/1.0", **(headers or {})}
    req = urllib.request.Request(url, headers=headers, data=data, method=method)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(req, timeout=30) as response:
            raw = response.read(MAX_RESPONSE + 1)
            status, retry = response.status, response.headers.get("Retry-After")
    except urllib.error.HTTPError as exc:
        raw = exc.read(MAX_RESPONSE + 1)
        status, retry = exc.code, exc.headers.get("Retry-After")
    except (urllib.error.URLError, TimeoutError, OSError):
        raise BrokerError("Broker connection failed; retry later. No credentials were logged.") from None
    if len(raw) > MAX_RESPONSE:
        raise BrokerError("Broker response exceeded the size limit.")
    try:
        payload = json.loads(raw)
    except (ValueError, UnicodeError):
        payload = {}
    if not isinstance(payload, dict):
        raise BrokerError("Broker returned an unexpected response format.")
    return status, payload, retry


def checked(status, payload):
    code = str(payload.get("errorCode", payload.get("code", "")))
    if status in (401, 403) or code in {"-8", "-15", "-16", "-17", "807", "808", "809", "810", "DH-901"}:
        raise BrokerError("Authentication expired or was rejected. Reconnect in the local login window.")
    if status == 429 or code in {"-429", "805", "DH-904"}:
        return "retry"
    if status >= 500 or code in {"800", "DH-908", "DH-909"}:
        return "retry"
    if status >= 400 or payload.get("s") == "error" or payload.get("status") == "error" or payload.get("errorCode"):
        raise BrokerError("Broker rejected the request. Check data subscription, instrument mapping and dates.")
    return "ok"


class Limiter:
    """Conservative rolling-window limits shared by every session request."""
    def __init__(self, broker, plan="standard", clock=time.monotonic, sleep=time.sleep):
        self.spacing = {"zerodha": 0.36, "dhan": 0.22, "fyers": 1.25}[broker]
        self.per_minute = 48 if broker == "fyers" else None
        self.per_day = {"zerodha": 100000, "dhan": 99000, "fyers": 4900}[broker]
        if broker == "fyers" and plan == "prime":
            self.spacing, self.per_minute, self.per_day = 0.13, 480, 490000
        self.clock, self.sleep = clock, sleep
        self.last = None
        self.minute, self.day = deque(), deque()
        self.lock = threading.Lock()

    def wait(self):
        with self.lock:
            now = self.clock()
            while self.day and now - self.day[0] >= 86400:
                self.day.popleft()
            if len(self.day) >= self.per_day:
                raise BrokerError("This helper reached its daily request budget. Resume after the limit window resets.")
            delay = max(0, self.spacing - (now - self.last)) if self.last is not None else 0
            while self.minute and now - self.minute[0] >= 60:
                self.minute.popleft()
            if self.per_minute and len(self.minute) >= self.per_minute:
                delay = max(delay, 60.1 - (now - self.minute[0]))
            if delay:
                self.sleep(delay)
            now = self.clock()
            self.last = now
            self.minute.append(now)
            self.day.append(now)


def required(fields, name):
    value = fields.get(name, "")
    if not isinstance(value, str) or not value.strip() or len(value) > 6000 or any(ord(c) < 32 for c in value):
        raise BrokerError("A required credential field is missing or invalid.")
    return value.strip()


class BrokerSession:
    def __init__(self, broker, identifier, token, plan="standard", request=transport, limiter=None):
        self.broker, self.identifier, self.token, self.plan = broker, identifier, token, plan
        self.request = request
        self.limiter = limiter or Limiter(broker, plan)
        self.active = True

    def clear(self):
        self.identifier = self.token = ""
        self.active = False

    def headers(self):
        if not self.active:
            raise BrokerError("Session closed. Reconnect in the local login window.")
        if self.broker == "zerodha":
            return {"X-Kite-Version": "3", "Authorization": "token " + self.identifier + ":" + self.token}
        if self.broker == "dhan":
            return {"access-token": self.token, "client-id": self.identifier}
        return {"Authorization": self.identifier + ":" + self.token}

    def call(self, method, url, body=None):
        headers = self.headers()
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode()
        for attempt in range(4):
            self.limiter.wait()
            status, payload, retry_after = self.request(method, url, headers, data)
            try:
                action = checked(status, payload)
            except BrokerError:
                if status in (401, 403) or str(payload.get("code", payload.get("errorCode", ""))) in {"-8", "-15", "-16", "-17", "807", "808", "809", "810", "DH-901"}:
                    self.clear()
                raise
            if action == "ok":
                return payload
            if attempt == 3:
                raise BrokerError("Broker remained rate-limited or unavailable after four attempts. Resume later.")
            # A bounded wait avoids indefinite hanging on an untrusted Retry-After.
            try:
                delay = float(retry_after) if retry_after is not None else 2 ** (attempt + 1)
            except (ValueError, TypeError):
                delay = 2 ** (attempt + 1)
            if not math.isfinite(delay) or delay > 60:
                raise BrokerError("Broker requested a long cooldown. Stop and resume after its limit resets.")
            self.limiter.sleep(max(1, delay))

    def verify(self):
        url = {"zerodha": "https://api.kite.trade/user/profile", "dhan": "https://api.dhan.co/v2/profile", "fyers": "https://api-t1.fyers.in/api/v3/profile"}[self.broker]
        payload = self.call("GET", url)
        if self.broker == "dhan" and str(payload.get("dhanClientId", "")) != self.identifier:
            self.clear()
            raise BrokerError("Dhan client ID does not match the access token.")

    def history(self, instrument, start, end):
        first, last = validate_range(start, end)
        if (last - first).days > 364:
            raise BrokerError("One history request may cover at most 365 calendar days.")
        kind = instrument.get("kind", "stock")
        if kind not in {"stock", "etf", "index"}:
            raise BrokerError("This research downloader supports cash stocks, ETFs and benchmark indices only.")
        if self.broker == "zerodha":
            token = str(instrument.get("zerodha_token", ""))
            if not re.fullmatch(r"[0-9]{1,15}", token):
                raise BrokerError("A numeric zerodha_token is required for each instrument.")
            query = urllib.parse.urlencode({"from": start + " 00:00:00", "to": end + " 23:59:59", "continuous": 0, "oi": 0})
            payload = self.call("GET", "https://api.kite.trade/instruments/historical/" + token + "/day?" + query)
            rows = payload.get("data", {}).get("candles")
        elif self.broker == "dhan":
            token = str(instrument.get("dhan_security_id", ""))
            segment = instrument.get("dhan_exchange_segment", "IDX_I" if kind == "index" else "NSE_EQ")
            if not re.fullmatch(r"[0-9]{1,15}", token) or segment not in {"NSE_EQ", "BSE_EQ", "IDX_I"}:
                raise BrokerError("Valid Dhan security ID and cash/index exchange segment are required.")
            payload = self.call("POST", "https://api.dhan.co/v2/charts/historical", {"securityId": token, "exchangeSegment": segment, "instrument": "INDEX" if kind == "index" else "EQUITY", "expiryCode": 0, "oi": False, "fromDate": start, "toDate": (last + dt.timedelta(days=1)).isoformat()})
            arrays = [payload.get(key) for key in ("timestamp", "open", "high", "low", "close", "volume")]
            if not all(isinstance(a, list) for a in arrays) or len({len(a) for a in arrays}) != 1:
                raise BrokerError("Dhan returned inconsistent candle arrays.")
            rows = list(zip(*arrays))
        else:
            symbol = instrument.get("fyers_symbol", "")
            if not isinstance(symbol, str) or not re.fullmatch(r"(?:NSE|BSE):[A-Za-z0-9_&. -]{1,80}", symbol):
                raise BrokerError("A valid cash or index fyers_symbol is required.")
            if self.plan == "standard" and first.year < dt.datetime.now(IST).year - 5:
                raise BrokerError("FYERS Standard daily history is limited to its rolling five-year plan window.")
            query = urllib.parse.urlencode({"symbol": symbol, "resolution": "D", "date_format": 1, "range_from": start, "range_to": end, "cont_flag": 0})
            payload = self.call("GET", "https://api-t1.fyers.in/data-rest/v3/history/?" + query)
            rows = payload.get("candles")
        return normalize_candles(rows, first, last)


def authenticate(fields, request=transport):
    broker = fields.get("broker")
    mode = fields.get("mode", "token")
    if broker not in {"zerodha", "dhan", "fyers"}:
        raise BrokerError("Choose Zerodha, Dhan or FYERS.")
    identifier = required(fields, "client_id")
    plan = fields.get("plan", "standard")
    if plan not in {"standard", "prime"}:
        raise BrokerError("Invalid data plan.")
    if mode == "code" and broker in {"zerodha", "fyers"}:
        secret, code = required(fields, "secret"), required(fields, "code")
        if broker == "zerodha":
            checksum = hashlib.sha256((identifier + code + secret).encode()).hexdigest()
            data = urllib.parse.urlencode({"api_key": identifier, "request_token": code, "checksum": checksum}).encode()
            status, payload, _ = request("POST", "https://api.kite.trade/session/token", {"X-Kite-Version": "3", "Content-Type": "application/x-www-form-urlencoded"}, data)
            checked(status, payload)
            token = payload.get("data", {}).get("access_token")
        else:
            hashed = hashlib.sha256((identifier + ":" + secret).encode()).hexdigest()
            data = json.dumps({"grant_type": "authorization_code", "appIdHash": hashed, "code": code}).encode()
            status, payload, _ = request("POST", "https://api-t1.fyers.in/api/v3/validate-authcode", {"Content-Type": "application/json"}, data)
            checked(status, payload)
            token = payload.get("access_token")
        if not isinstance(token, str) or not token or len(token) > 6000:
            raise BrokerError("Broker did not return an access token. Restart its login flow.")
    elif mode == "token":
        token = required(fields, "access_token")
    else:
        raise BrokerError("Unsupported login method for this broker.")
    session = BrokerSession(broker, identifier, token, plan, request=request)
    try:
        session.verify()
    except Exception:
        session.clear()
        raise
    return session


def validate_range(start, end, today=None):
    try:
        first, last = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    except (ValueError, TypeError):
        raise BrokerError("Dates must use YYYY-MM-DD.") from None
    today = today or dt.datetime.now(IST).date()
    if first > last or first < dt.date(1990, 1, 1) or last >= today:
        raise BrokerError("Use an ordered range from 1990 onward ending before today in Asia/Kolkata; partial daily bars are excluded.")
    return first, last


def normalize_candles(rows, first, last):
    if not isinstance(rows, list):
        raise BrokerError("Broker returned no candle array.")
    unique = {}
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) < 6:
            raise BrokerError("Broker returned a malformed candle.")
        try:
            if isinstance(row[0], str):
                stamp = dt.datetime.fromisoformat(row[0].replace("Z", "+00:00"))
                date = stamp.astimezone(IST).date() if stamp.tzinfo else stamp.date()
            else:
                date = dt.datetime.fromtimestamp(float(row[0]), IST).date()
            values = [float(x) for x in row[1:6]]
        except (TypeError, ValueError, OverflowError, OSError):
            raise BrokerError("Broker returned an invalid timestamp or numeric value.") from None
        o, h, low, c, volume = values
        if not all(math.isfinite(x) for x in values) or min(o, h, low, c) <= 0 or volume < 0 or h < max(o, c, low) or low > min(o, c, h):
            raise BrokerError("Candle failed price, range or volume validation; no adjusted values were invented.")
        if not first <= date <= last:
            raise BrokerError("Broker returned a candle outside the requested date range.")
        item = dict(zip(("date", "open", "high", "low", "close", "volume"), (date.isoformat(), *values)))
        if item["date"] in unique and unique[item["date"]] != item:
            raise BrokerError("Broker returned conflicting duplicate daily candles.")
        unique[item["date"]] = item
    return [unique[key] for key in sorted(unique)]
