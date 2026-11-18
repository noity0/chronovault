"""
ChronoVault Oracle — Accuracy Engine
====================================
Makes the Oracle measurably accurate instead of confidently wrong:
  1. Brier scoring      — score every prediction (0 = perfect, 2 = worst)
  2. Calibration table  — turn raw confidence into TRUSTED confidence from history
  3. Ensemble boost     — N independent sources agree -> confidence up
  4. Backtesting        — test forecasting models on Vault history BEFORE answering
  5. Exact-first routing helper — SIMULATE beats PREDICT whenever math can decide
Stdlib only. No API keys. Ever.
"""
import json
import math
import os
import statistics


# ------------------------------------------------------------------ scoring
def brier(confidence: float, outcome: bool) -> float:
    """Brier score: (p - outcome)^2. 0 = perfect, 1 = useless, 2 = inverted."""
    p = min(max(confidence, 0.0), 1.0)
    return (p - (1.0 if outcome else 0.0)) ** 2


def engine_report(prophecies: list) -> dict:
    """Aggregate per-engine accuracy from the Paradox Ledger."""
    by_engine = {}
    for pr in prophecies:
        if pr.get("status") not in ("fulfilled", "violated"):
            continue
        eng = pr.get("engine", "?")
        ok = pr["status"] == "fulfilled"
        e = by_engine.setdefault(eng, {"n": 0, "brier": 0.0, "hits": 0})
        e["n"] += 1
        e["hits"] += int(ok)
        e["brier"] += brier(float(pr.get("confidence", 0.5)), ok)
    for eng, e in by_engine.items():
        e["brier"] = round(e["brier"] / e["n"], 4)
        e["hit_rate"] = round(e["hits"] / e["n"], 3)
        e["sach_rate"] = f"{round(100 * e['hit_rate'])}%"
    return by_engine


# -------------------------------------------------------------- calibration
def calibration_table(prophecies: list, bins: int = 10) -> list:
    """Empirical calibration: predicted-confidence-bucket -> actual hit rate."""
    rows = [[] for _ in range(bins)]
    for pr in prophecies:
        if pr.get("status") not in ("fulfilled", "violated"):
            continue
        c = min(max(float(pr.get("confidence", 0.5)), 0.0), 0.999)
        i = int(c * bins)
        rows[i].append(pr["status"] == "fulfilled")
    table = []
    for i, xs in enumerate(rows):
        center = round((i + 0.5) / bins, 3)
        if xs:
            table.append({"bin": center, "empirical": round(statistics.mean(xs), 3),
                          "n": len(xs)})
        else:
            table.append({"bin": center, "empirical": None, "n": 0})
    return table


def calibrated_confidence(raw: float, table: list) -> float:
    """Look up the empirical hit rate for this confidence bucket; blend toward it."""
    if not table:
        return raw
    bucket = min(max(int(raw * len(table)), 0), len(table) - 1)
    emp = table[bucket]["empirical"]
    if emp is None or table[bucket]["n"] < 5:
        return raw  # not enough data to correct yet
    w = min(1.0, table[bucket]["n"] / 30.0)  # trust grows with sample size
    return round((1 - w) * raw + w * emp, 3)


# ----------------------------------------------------------------- ensemble
def ensemble_confidence(agreement: float, base: float = 0.7) -> float:
    """agreement = fraction of sources giving the identical answer (0..1)."""
    a = min(max(agreement, 0.0), 1.0)
    return round(min(0.98, base + (1 - base) * a), 3)


# --------------------------------------------------------------- backtesting
def mape(actual: list, predicted: list) -> float:
    """Mean absolute percentage error for backtesting growth forecasts."""
    pairs = [(a, p) for a, p in zip(actual, predicted)
             if isinstance(a, (int, float)) and a not in (0, None)
             and isinstance(p, (int, float))]
    if not pairs:
        return float("inf")
    return round(100 * statistics.mean(abs(a - p) / abs(a) for a, p in pairs), 2)


def backtest(model_fn, series: list, horizon: int = 7) -> dict:
    """Walk-forward backtest: model_fn(history) -> next value. series = ordered numbers."""
    if len(series) < horizon + 3:
        return {"ok": False, "reason": "not enough history"}
    acts, preds = [], []
    for i in range(horizon, len(series)):
        hist = series[:i]
        try:
            preds.append(model_fn(hist))
            acts.append(series[i])
        except Exception:
            continue
    err = mape(acts, preds)
    grade = ("excellent" if err < 5 else
             "good" if err < 12 else
             "fair" if err < 25 else "weak")
    return {"ok": True, "mape": err, "grade": grade,
            "confidence": round(min(0.95, max(0.2, 1 - err / 100)), 2)}


# ------------------------------------------------------------ exact routing
def route(question_lower: str, time_coord: str) -> str:
    """SIMULATE > PROBE > PREDICT preference, per 04_ORACLE.md routing table."""
    future = time_coord == "future"
    math_markers = ("day", "din", "what day", "konsa", "loan", "emi", "interest",
                    "compound", "percentage", "birthday")
    file_markers = ("folder", "file", "size", "storage", "disk", "kb", "mb", "gb")
    web_markers = ("news", "weather", "price", "match", "headline", "bitcoin")
    if any(m in question_lower for m in math_markers):
        return "SIMULATE" if future else "VAULT"
    if future:
        if any(m in question_lower for m in web_markers):
            return "PROBE"
        if any(m in question_lower for m in file_markers):
            return "PREDICT+PROBE"
        return "PREDICT+PROBE"
    return "VAULT"


if __name__ == "__main__":
    demo = [
        {"engine": "PREDICT", "confidence": 0.8, "status": "fulfilled"},
        {"engine": "PREDICT", "confidence": 0.8, "status": "violated"},
        {"engine": "SIMULATE", "confidence": 0.99, "status": "fulfilled"},
        {"engine": "PREDICT", "confidence": 0.9, "status": "fulfilled"},
    ]
    print(json.dumps(engine_report(demo), indent=1))
    print("calibration:", calibration_table(demo, 10)[:3])
    print("ensemble 3/3 agree:", ensemble_confidence(1.0))
    print("backtest:", backtest(lambda h: h[-1], [10, 12, 13, 15, 16, 18, 19, 21, 22], 3))
    print("route('what day 2050'):", route("what day konsa birthday", "future"))
