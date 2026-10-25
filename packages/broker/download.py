"""Download daily history through an already authenticated local helper."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

from broker_core import BrokerError, IST, NoRedirect, validate_range

VERSION = "1.0.0"
SYMBOL = re.compile(r"[A-Za-z0-9][A-Za-z0-9_&.-]{0,79}")
BENCHMARKS = {"NIFTY_500", "NIFTY_50"}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    with open(temporary, "wb") as handle:
        handle.write(encoded(value))
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


class LocalClient:
    def __init__(self, session_url):
        parsed = urllib.parse.urlsplit(session_url)
        try:
            port = parsed.port
        except ValueError:
            raise BrokerError("Invalid local session URL.") from None
        if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or not port or parsed.username or parsed.password or parsed.query or parsed.fragment or not re.fullmatch(r"/session/[A-Za-z0-9_-]{40,64}", parsed.path):
            raise BrokerError("Use the exact http://127.0.0.1:PORT/session/... reference from the local helper.")
        self.base = session_url.rstrip("/")
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def call(self, route, body=None):
        headers = {"X-SkillsGuild-Request": "history-client", "Accept": "application/json"}
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = encoded(body)
        request = urllib.request.Request(self.base + route, headers=headers, data=data, method="POST" if body is not None else "GET")
        try:
            with self.opener.open(request, timeout=250) as response:
                raw = response.read(16 * 1024 * 1024 + 1)
        except urllib.error.HTTPError as exc:
            # The helper emits only fixed, sanitized errors. Never echo arbitrary
            # broker bodies, request URLs, headers or exception representations.
            try:
                detail = json.loads(exc.read(16384)).get("error", "Local request rejected.")
            except (ValueError, AttributeError):
                detail = "Local request rejected."
            raise BrokerError(str(detail)[:300]) from None
        except (urllib.error.URLError, OSError, TimeoutError):
            raise BrokerError("Cannot reach the local helper. Keep it running and reconnect if necessary.") from None
        if len(raw) > 16 * 1024 * 1024:
            raise BrokerError("Local response exceeded the size limit.")
        try:
            payload = json.loads(raw)
        except ValueError:
            raise BrokerError("Invalid local response.") from None
        if not isinstance(payload, dict):
            raise BrokerError("Unexpected local response.")
        return payload


def read_instruments(path, broker):
    try:
        with open(path, newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise BrokerError("Instrument CSV needs unique column names.")
            allowed = {"symbol", "kind", "industry", "zerodha_token", "dhan_security_id", "dhan_exchange_segment", "fyers_symbol"}
            if not {"symbol", "kind", "industry"}.issubset(reader.fieldnames) or not set(reader.fieldnames).issubset(allowed):
                raise BrokerError("Use the supplied instrument CSV columns. Credentials never belong in this file.")
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error):
        raise BrokerError("Cannot read the instrument mapping CSV.") from None
    if not 1 <= len(rows) <= 5000:
        raise BrokerError("Provide between 1 and 5000 mapped instruments.")
    items = {}
    mapping_key = {"zerodha": "zerodha_token", "dhan": "dhan_security_id", "fyers": "fyers_symbol"}[broker]
    for raw in rows:
        if None in raw or any(value is None for value in raw.values()):
            raise BrokerError("Instrument CSV contains a malformed row.")
        item = {key: value.strip() for key, value in raw.items() if value.strip()}
        symbol = item.get("symbol", "")
        # Windows device names remain reserved even when followed by extensions.
        if not SYMBOL.fullmatch(symbol) or symbol.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *["COM" + str(i) for i in range(1, 10)], *["LPT" + str(i) for i in range(1, 10)]}:
            raise BrokerError("A symbol is not safe for a local data filename.")
        if symbol.upper() in {key.upper() for key in items}:
            raise BrokerError("Instrument CSV contains a duplicate symbol.")
        if item.get("kind") not in {"stock", "etf", "index"} or not item.get(mapping_key):
            raise BrokerError("Every instrument needs a cash/index kind and a broker-specific mapping.")
        if item["kind"] == "stock" and not item.get("industry"):
            raise BrokerError("Each stock requires an industry for industry-aware strategies.")
        if symbol in BENCHMARKS and item["kind"] != "index":
            raise BrokerError("NIFTY_500 and NIFTY_50 must be mapped as indices.")
        items[symbol] = item
    if not BENCHMARKS.issubset(items):
        raise BrokerError("Map both NIFTY_500 and NIFTY_50 explicitly; benchmark broker identifiers are never guessed.")
    return items


def chunks(first, last):
    while first <= last:
        end = min(first + dt.timedelta(days=364), last)
        yield first.isoformat(), end.isoformat()
        first = end + dt.timedelta(days=1)


def validate_rows(rows, start, end):
    if not isinstance(rows, list):
        raise BrokerError("Cached or downloaded candles are not a list.")
    previous = ""
    for item in rows:
        if not isinstance(item, dict) or set(item) != {"date", "open", "high", "low", "close", "volume"}:
            raise BrokerError("Cached or downloaded candle schema is invalid.")
        date = item["date"]
        if not isinstance(date, str) or not start <= date <= end or date <= previous:
            raise BrokerError("Cached or downloaded dates are unsorted, duplicate or outside the requested range.")
        try:
            dt.date.fromisoformat(date)
            values = [float(item[k]) for k in ("open", "high", "low", "close", "volume")]
        except (TypeError, ValueError):
            raise BrokerError("Invalid candle data.") from None
        o, h, low, c, volume = values
        if not all(math.isfinite(x) for x in values) or min(o, h, low, c) <= 0 or volume < 0 or h < max(o, c, low) or low > min(o, c, h):
            raise BrokerError("Invalid candle values.")
        previous = date
    return rows


def download_dataset(client, instruments, start, end, output, progress=print):
    first, last = validate_range(start, end)
    status = client.call("/status")
    broker = status.get("broker")
    if not status.get("connected") or broker not in {"zerodha", "dhan", "fyers"}:
        raise BrokerError("The local broker session is not connected.")
    items = read_instruments(instruments, broker)
    output = Path(output).expanduser().resolve()
    # Public source checkout is not a market-data cache.
    source = Path(__file__).resolve()
    repository = next((p for p in source.parents if (p / ".git").exists()), None)
    if repository and (output == repository or repository in output.parents):
        raise BrokerError("Choose a private data directory outside the source repository.")
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    identity = {"version": VERSION, "broker": broker, "from": start, "to": end, "instruments": items}
    identity_hash = digest(encoded(identity))
    identity_file = output / "download-request.json"
    if identity_file.exists():
        if digest(identity_file.read_bytes()) != digest(encoded(identity)):
            raise BrokerError("This directory belongs to a different broker, mapping or date range. Choose a new output directory.")
    else:
        if any(output.iterdir()):
            raise BrokerError("Output directory is nonempty and has no matching download request. Choose a new directory.")
        write_json(identity_file, identity)
    manifest = {"version": VERSION, "request_sha256": identity_hash, "broker": broker, "plan": status.get("plan"), "interval": "day", "timezone": "Asia/Kolkata", "requested_from": start, "requested_to": end, "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(), "state": "downloading", "corporate_action_adjustment": "provider supplied; not independently verified", "universe": "user-supplied mapping; not a point-in-time membership database", "redistribution": "private user data; broker/exchange terms apply", "files": {}, "coverage": {}, "warnings": ["A successful request does not certify complete trading-calendar coverage.", "Broker history, revisions and current instrument mappings can differ from the published research dataset."]}
    write_json(output / "data-manifest.json", manifest)
    all_rows = {}
    for number, (symbol, item) in enumerate(items.items(), 1):
        combined = []
        for chunk_start, chunk_end in chunks(first, last):
            cache_key = digest(encoded({"broker": broker, "instrument": item, "from": chunk_start, "to": chunk_end, "version": VERSION}))
            cache_path = output / ".cache" / (cache_key + ".json")
            if cache_path.exists():
                cached = json.loads(cache_path.read_text(encoding="utf-8"))
                rows = cached.get("candles")
                if cached.get("sha256") != digest(encoded(rows)):
                    raise BrokerError("Cached candle hash failed. Keep the corrupted file for diagnosis and use a new data directory.")
            else:
                rows = client.call("/history", {"instrument": item, "from": chunk_start, "to": chunk_end}).get("candles")
                validate_rows(rows, chunk_start, chunk_end)
                write_json(cache_path, {"sha256": digest(encoded(rows)), "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(), "candles": rows})
            combined.extend(validate_rows(rows, chunk_start, chunk_end))
        validate_rows(combined, start, end)
        all_rows[symbol] = combined
        data_file = output / "data" / (symbol + ".json")
        write_json(data_file, combined)
        manifest["files"]["data/" + symbol + ".json"] = digest(data_file.read_bytes())
        manifest["coverage"][symbol] = {"bars": len(combined), "first": combined[0]["date"] if combined else None, "last": combined[-1]["date"] if combined else None}
        write_json(output / "data-manifest.json", manifest)
        progress(f"{number}/{len(items)} {symbol}: {len(combined)} daily bars cached")
    if any(not all_rows[key] for key in BENCHMARKS):
        raise BrokerError("A required benchmark returned no history. Dataset remains incomplete; check its mapping and plan.")
    benchmark_dates = {row["date"] for row in all_rows["NIFTY_500"]}
    reasons = {}
    # Reject whole-series price/empty-data problems before computing the same
    # minimum-stock calendar as research/panel.py. Index-only special sessions
    # must not turn into an internal gap in every otherwise sound stock.
    for symbol, rows in all_rows.items():
        if symbol in BENCHMARKS:
            continue
        flags = []
        if not rows:
            flags.append("no returned history")
        elif any(abs(rows[i]["close"] / rows[i-1]["close"] - 1) > 0.40 for i in range(1, len(rows))):
            flags.append("close-to-close move above 40%; review corporate actions before inclusion")
        if flags:
            reasons[symbol] = flags
    counts = Counter(row["date"] for symbol, rows in all_rows.items()
                     if items[symbol]["kind"] == "stock" and symbol not in reasons for row in rows)
    shared_dates = {date for date in benchmark_dates if counts[date] >= 100}
    for symbol, rows in all_rows.items():
        if not rows or symbol in BENCHMARKS:
            continue
        returned = {row["date"] for row in rows}
        missing = sorted(date for date in benchmark_dates if rows[0]["date"] <= date <= rows[-1]["date"] and date not in returned)
        effective_missing = [date for date in missing if date in shared_dates]
        manifest["coverage"][symbol]["internal_dates_missing_vs_nifty500"] = missing
        manifest["coverage"][symbol]["internal_dates_missing_on_shared_calendar"] = effective_missing
        if effective_missing:
            reasons.setdefault(symbol, []).append("internal daily gaps on the >=100-stock shared calendar; review trading suspensions and provider gaps")
    # Whole-series quarantine can itself reduce coverage. Record the final
    # calendar the runner will retain, without deleting original broker rows.
    final_counts = Counter(row["date"] for symbol, rows in all_rows.items()
                           if items[symbol]["kind"] == "stock" and symbol not in reasons for row in rows)
    retained_dates = {date for date in benchmark_dates if final_counts[date] >= 100}
    manifest["calendar_minimum_stock_bars"] = 100
    manifest["omitted_incomplete_sessions"] = [{"date": date, "stock_bars": final_counts[date]} for date in sorted(benchmark_dates - retained_dates)]
    manifest["retained_shared_sessions"] = len(retained_dates)
    if not retained_dates:
        manifest["warnings"].append("No session has 100 eligible stock histories; this dataset cannot run the current portfolio strategies.")
    if not retained_dates.issubset({row["date"] for row in all_rows["NIFTY_50"]}):
        raise BrokerError("NIFTY_50 is missing retained shared sessions. Dataset remains incomplete; verify benchmark mappings and history.")
    universe = {"items": items, "source": "user-supplied broker mapping", "point_in_time_membership": False}
    quarantine = {"symbols": sorted(reasons), "reasons": reasons, "policy": "Conservative download checks only; independently review corporate actions and historical membership before interpreting performance."}
    write_json(output / "Universe.json", universe)
    write_json(output / "Data-quality-quarantine.json", quarantine)
    for name in ("Universe.json", "Data-quality-quarantine.json"):
        manifest["files"][name] = digest((output / name).read_bytes())
    manifest["state"] = "downloaded-needs-research-validation"
    manifest["quarantined_symbols"] = sorted(reasons)
    write_json(output / "data-manifest.json", manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", required=True, help="Opaque local session URL; never a broker access token")
    parser.add_argument("--instruments", required=True, help="Local CSV of broker mappings and industries")
    parser.add_argument("--from", dest="start", required=True)
    parser.add_argument("--to", dest="end", required=True)
    parser.add_argument("--output", required=True, help="Private dataset directory outside this repository")
    args = parser.parse_args()
    try:
        result = download_dataset(LocalClient(args.session), args.instruments, args.start, args.end, args.output)
        print("Download complete. Review data-manifest.json and quarantine before research. Quarantined instruments: " + str(len(result["quarantined_symbols"])))
    except (BrokerError, OSError, ValueError) as exc:
        print("Download stopped: " + (str(exc) if isinstance(exc, BrokerError) else "Local data could not be read or written."), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
