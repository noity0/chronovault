"""ChronoVault 2.0 — honest forecasting.

No black box, no fake certainty:
  * naive persistence, linear drift, mean reversion, exponential smoothing
  * walk-forward backtest on the actual history
  * best model by MAE, prediction interval from residual spread
  * confidence based on skill vs naive + data length + directional accuracy
"""
from __future__ import annotations

import math
import statistics
from datetime import date, datetime, timedelta


def _parse_day(s: str) -> date:
    return date.fromisoformat(s[:10])


def prepare(series: list[tuple[str, float]]) -> tuple[list[int], list[float]]:
    pts = []
    for d, v in series:
        try:
            pts.append((_parse_day(d), float(v)))
        except Exception:
            continue
    pts.sort()
    if not pts:
        return [], []
    t0 = pts[0][0]
    xs = [(d - t0).days for d, _ in pts]
    ys = [v for _, v in pts]
    # collapse duplicate days
    cx, cy = [], []
    for x, y in zip(xs, ys):
        if cx and x == cx[-1]:
            cy[-1] = y
        else:
            cx.append(x)
            cy.append(y)
    return cx, cy


def _linear_fit(xs: list[int], ys: list[float]) -> tuple[float, float]:
    n = len(xs)
    if n < 2:
        return 0.0, ys[-1] if ys else 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return 0.0, my
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    return slope, my - slope * mx


def _ema(ys: list[float], alpha: float = 0.3) -> float:
    if not ys:
        return 0.0
    v = ys[0]
    for y in ys[1:]:
        v = alpha * y + (1 - alpha) * v
    return v


def _predict(model: str, xs: list[int], ys: list[float], target_t: int) -> float:
    last = ys[-1]
    last_t = xs[-1]
    if model == "naive":
        return last
    if model == "drift":
        slope, intercept = _linear_fit(xs, ys)
        # damp long extrapolations slightly
        raw = intercept + slope * target_t
        steps = max(0, target_t - last_t)
        damp = 0.92 ** max(0, steps / 30.0)
        return last + (raw - last) * damp
    if model == "meanrev":
        window = ys[-30:] if len(ys) >= 10 else ys
        mean = sum(window) / len(window)
        steps = max(0, target_t - last_t)
        return mean + (last - mean) * (0.94 ** max(0, steps / 3.0))
    if model == "ema":
        return _ema(ys)
    return last


def forecast(series: list[tuple[str, float]], horizon_days: int = 30) -> dict | None:
    xs, ys = prepare(series)
    n = len(ys)
    if n < 6:
        return None
    gaps = [b - a for a, b in zip(xs, xs[1:]) if b > a]
    step = statistics.median(gaps) if gaps else 1
    step = max(1.0, step)
    target_t = xs[-1] + max(1, int(round(horizon_days / step))) * int(step)
    h = max(1, int(round(horizon_days / step)))

    models = ["naive", "drift", "meanrev", "ema"]
    k = min(20, max(4, n // 6))
    errors: dict[str, list[float]] = {m: [] for m in models}
    hits: dict[str, list[int]] = {m: [] for m in models}
    for i in range(n - k, n):
        tx, ty = xs[:i], ys[:i]
        if len(tx) < 4:
            continue
        actual = ys[i]
        for m in models:
            p = _predict(m, tx, ty, xs[i])
            errors[m].append(abs(p - actual))
            if abs(actual - ty[-1]) > 1e-12:
                hits[m].append(1 if (p - ty[-1]) * (actual - ty[-1]) > 0 else 0)
    maes = {m: (sum(v) / len(v) if v else float("inf")) for m, v in errors.items()}
    best = min(models, key=lambda m: maes[m])
    if not math.isfinite(maes[best]):
        best = "naive"
    pred = _predict(best, xs, ys, target_t)
    naive_mae = maes["naive"] if math.isfinite(maes["naive"]) else 0.0
    skill = 0.0 if naive_mae <= 0 else max(-1.0, 1.0 - maes[best] / naive_mae)
    resid = errors[best] or [abs(ys[i] - ys[i - 1]) for i in range(1, n)]
    sigma = statistics.pstdev(resid) if len(resid) > 1 else abs(pred) * 0.02
    band = 1.96 * sigma * math.sqrt(max(1, h))
    dir_acc = (sum(hits[best]) / len(hits[best])) if hits[best] else 0.5
    conf = 0.32 + 0.30 * max(0.0, skill) + 0.12 * min(1.0, n / 120) + \
        0.12 * (dir_acc - 0.5) * 2
    conf = max(0.24, min(0.84, conf))
    lo, hi = pred - band, pred + band
    dec = 0 if abs(pred) >= 1000 else (2 if abs(pred) >= 10 else 4)
    last_date = date.fromisoformat(series[-1][0][:10])
    return {
        "model": best,
        "model_note": {
            "naive": "persistence (kal = aaj)",
            "drift": "linear drift (trend)",
            "meanrev": "mean reversion",
            "ema": "exponential smoothing",
        }[best],
        "last": round(ys[-1], dec),
        "predicted": round(pred, dec),
        "lo": round(lo, dec),
        "hi": round(hi, dec),
        "horizon_days": horizon_days,
        "target_date": (last_date + timedelta(days=horizon_days)).isoformat(),
        "n": n,
        "step_days": step,
        "mae": round(maes[best], dec),
        "naive_mae": round(naive_mae, dec),
        "skill": round(skill, 3),
        "direction_accuracy": round(dir_acc, 3),
        "confidence": round(conf, 3),
        "band_pct": round((band / pred * 100) if pred else 0, 2),
        "change_pct": round(((pred - ys[-1]) / ys[-1] * 100) if ys[-1] else 0, 2),
    }


def to_text(label: str, f: dict, unit: str = "") -> str:
    def fmt(v):
        if abs(v) >= 1000:
            return f"{v:,.0f}"
        if abs(v) >= 10:
            return f"{v:,.2f}"
        return f"{v:,.4f}"
    arrow = "^" if f["predicted"] > f["last"] else ("v" if f["predicted"] < f["last"] else "->")
    u = (" " + unit) if unit else ""
    return (
        f"{label}: abhi {fmt(f['last'])}{u}. {f['horizon_days']} din ka forecast: "
        f"{fmt(f['predicted'])}{u} {arrow} ({f['change_pct']:+.1f}%), range "
        f"{fmt(f['lo'])}–{fmt(f['hi'])}{u}. Model: {f['model_note']}; "
        f"confidence {int(f['confidence'] * 100)}%. Yeh statistical projection hai, "
        f"guarantee nahi."
    )
