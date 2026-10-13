"""Offline daily breakout/volume baseline. Standard library only; never sends orders.

Input CSV: exchange,symbol,session,open,high,low,close,volume.
Calendar CSV: session,close_at (offset-aware timestamp, supplied exchange calendar).
The caller is responsible for correct session coverage and corporate adjustments.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import date, datetime
from pathlib import Path
from statistics import fmean


def aware_time(value: str) -> datetime:
    result = datetime.fromisoformat(value)
    if result.utcoffset() is None:
        raise ValueError("as-of and close_at timestamps must include an offset")
    return result


def read_calendar(path: Path) -> dict[str, datetime]:
    calendar = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            session = date.fromisoformat(row["session"]).isoformat()
            if session in calendar:
                raise ValueError(f"duplicate calendar session: {session}")
            calendar[session] = aware_time(row["close_at"])
    if not calendar:
        raise ValueError("calendar is empty")
    return calendar


def read_prices(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            clean = {key: row[key].strip() for key in ("exchange", "symbol", "session")}
            date.fromisoformat(clean["session"])
            if not clean["exchange"] or not clean["symbol"]:
                raise ValueError("exchange and symbol are required")
            for key in ("open", "high", "low", "close", "volume"):
                clean[key] = float(row[key])
                if not math.isfinite(clean[key]):
                    raise ValueError(f"nonfinite {key}: {clean['session']}")
            if not (0 < clean["low"] <= min(clean["open"], clean["close"])
                    <= max(clean["open"], clean["close"]) <= clean["high"]):
                raise ValueError(f"invalid OHLC: {clean['session']}")
            if clean["volume"] < 0:
                raise ValueError(f"negative volume: {clean['session']}")
            rows.append(clean)
    return rows


def calculate(rows: list[dict], calendar: dict[str, datetime], as_of: datetime,
              lookback: int = 252, volume_lookback: int = 20,
              near_pct: float = 3, volume_threshold: float = 2, buffer_pct: float = 0) -> list[dict]:
    if lookback < 1 or volume_lookback < 1:
        raise ValueError("lookbacks must be positive")
    if not math.isfinite(near_pct) or not 0 <= near_pct <= 100:
        raise ValueError("near_pct must be finite and between 0 and 100")
    if not math.isfinite(volume_threshold) or volume_threshold <= 0:
        raise ValueError("volume_threshold must be positive and finite")
    if not math.isfinite(buffer_pct) or buffer_pct < 0:
        raise ValueError("buffer_pct must be finite and nonnegative")
    if as_of.utcoffset() is None:
        raise ValueError("as_of must include an offset")
    sessions = sorted(s for s, close_at in calendar.items() if close_at <= as_of)
    groups: dict[tuple[str, str], dict[str, dict]] = {}
    for row in rows:
        key = (row["exchange"], row["symbol"])
        if row["session"] not in calendar:
            raise ValueError(f"session absent from supplied calendar: {row['session']}")
        group = groups.setdefault(key, {})
        if row["session"] in group:
            raise ValueError(f"duplicate price row: {key} {row['session']}")
        group[row["session"]] = row

    output = []
    for (exchange, symbol), group in sorted(groups.items()):
        for index, session in enumerate(sessions):
            # Missing sessions are visible exclusions, never compressed windows.
            row = group.get(session)
            result = {"exchange": exchange, "symbol": symbol, "session": session,
                      "signal_timestamp": calendar[session].isoformat(),
                      "lookback": lookback, "volume_lookback": volume_lookback,
                      "near_pct": near_pct, "volume_threshold": volume_threshold,
                      "data_quality": "ok", "reference_high": None,
                      "reference_low": None, "close": None, "distance_to_high_pct": None,
                      "breakout": None, "near_high": None, "breakdown": None,
                      "baseline_volume": None, "rvol": None, "volume_breakout": None}
            result.update(reference_start=None,reference_end=None,lookback_mode="sessions",
                          history_count=sum(day in group for day in sessions[max(0,index-lookback):index]),
                          distance_above_pct=None,distance_pct=None,rank=None,buffer_pct=buffer_pct)
            if row is None:
                result["data_quality"] = "missing_current_session"
                output.append(result)
                continue
            result["close"] = row["close"]
            if index < max(lookback, volume_lookback):
                result["data_quality"] = "insufficient_history"
                output.append(result)
                continue
            previous = sessions[index - max(lookback, volume_lookback):index]
            if any(day not in group for day in previous):
                result["data_quality"] = "missing_reference_session"
                output.append(result)
                continue
            price_rows = [group[day] for day in sessions[index-lookback:index]]
            volume_rows = [group[day] for day in sessions[index-volume_lookback:index]]
            high = max(item["high"] for item in price_rows)
            low = min(item["low"] for item in price_rows)
            baseline = fmean(item["volume"] for item in volume_rows)
            distance = 100 * (high - row["close"]) / high
            result.update(reference_high=high, reference_low=low,
                          distance_to_high_pct=distance,
                          breakout=row["close"] > high*(1+buffer_pct/100),
                          near_high=0 <= distance <= near_pct,
                          breakdown=row["close"] < low, baseline_volume=baseline)
            result.update(reference_start=sessions[index-lookback],reference_end=sessions[index-1],
                          distance_above_pct=-distance,distance_pct=distance)
            if baseline > 0:
                result["rvol"] = row["volume"] / baseline
                result["volume_breakout"] = result["rvol"] >= volume_threshold
            else:
                result["data_quality"] = "zero_volume_baseline"
            output.append(result)
    for session in sessions:
        near=sorted((row for row in output if row['session']==session and row['near_high']),
                    key=lambda row:(row['distance_pct'],row['exchange'],row['symbol']))
        for rank,row in enumerate(near,1):row['rank']=rank
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prices", type=Path)
    parser.add_argument("--calendar", required=True, type=Path)
    parser.add_argument("--as-of", required=True, type=aware_time)
    parser.add_argument("--lookback", type=int, default=252)
    parser.add_argument("--volume-lookback", type=int, default=20)
    parser.add_argument("--near-pct", type=float, default=3)
    parser.add_argument("--volume-threshold", type=float, default=2)
    parser.add_argument("--buffer-pct", type=float, default=0)
    parser.add_argument("--output-prefix", type=Path, default=Path("signals"))
    args = parser.parse_args()
    results = calculate(read_prices(args.prices), read_calendar(args.calendar), args.as_of,
                        args.lookback, args.volume_lookback, args.near_pct, args.volume_threshold, args.buffer_pct)
    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    args.output_prefix.with_suffix(".json").write_text(
        json.dumps(results, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    if results:
        with args.output_prefix.with_suffix(".csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(results[0]))
            writer.writeheader()
            writer.writerows(results)
    print(f"Wrote {len(results)} observation/exclusion rows; no broker connection or orders.")


if __name__ == "__main__":
    main()
